#  Author:   Niels Nuyttens  <niels@nannyml.com>
#
#  License: Apache Software License 2.0
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from nannyml._typing import ModelOutputsType, ProblemType
from nannyml.base import _list_missing
from nannyml.calibration import Calibrator, needs_calibration
from nannyml.chunk import Chunk, Chunker
from nannyml.exceptions import InvalidArgumentsException
from nannyml.performance_estimation.confidence_based import CBPE
from nannyml.performance_estimation.confidence_based.cbpe import _create_multilevel_index
from nannyml.performance_estimation.confidence_based.results import Result
from nannyml.sampling_error import SAMPLING_ERROR_RANGE


class _BinaryClassificationCBPE(CBPE):
    def __init__(
        self,
        metrics: List[str],
        y_pred: str,
        y_pred_proba: ModelOutputsType,
        y_true: str,
        problem_type: Union[str, ProblemType],
        timestamp_column_name: Optional[str] = None,
        chunk_size: Optional[int] = None,
        chunk_number: Optional[int] = None,
        chunk_period: Optional[str] = None,
        chunker: Optional[Chunker] = None,
        calibration: Optional[str] = None,
        calibrator: Optional[Calibrator] = None,
    ):
        """Creates a new CBPE performance estimator."""
        super().__init__(
            y_pred=y_pred,
            y_pred_proba=y_pred_proba,
            y_true=y_true,
            timestamp_column_name=timestamp_column_name,
            problem_type=problem_type,
            metrics=metrics,
            chunk_size=chunk_size,
            chunk_number=chunk_number,
            chunk_period=chunk_period,
            chunker=chunker,
            calibration=calibration,
            calibrator=calibrator,
        )

        if not isinstance(y_pred_proba, str):
            raise InvalidArgumentsException(
                f"'y_pred_proba' is of type '{type(y_pred_proba)}'. "
                f"Binary use cases require 'y_pred_proba' to be a string."
            )
        self.y_pred_proba: str = y_pred_proba  # redeclare as str type to ease mypy

        self.confidence_upper_bound = 1
        self.confidence_lower_bound = 0

        self.result: Optional[Result] = None

    def _fit(self, reference_data: pd.DataFrame, *args, **kwargs) -> CBPE:
        """Fits the drift calculator using a set of reference data."""
        if reference_data.empty:
            raise InvalidArgumentsException('data contains no rows. Please provide a valid data set.')

        _list_missing([self.y_true, self.y_pred_proba, self.y_pred], list(reference_data.columns))

        # We need uncalibrated data to calculate the realized performance on.
        # We need realized performance in threshold calculations.
        # https://github.com/NannyML/nannyml/issues/98
        reference_data[f'uncalibrated_{self.y_pred_proba}'] = reference_data[self.y_pred_proba]

        for metric in self.metrics:
            metric.fit(reference_data)

        # Fit calibrator if calibration is needed
        aligned_reference_data = reference_data.reset_index(drop=True)  # fix mismatch between data and shuffle split
        self.needs_calibration = needs_calibration(
            y_true=aligned_reference_data[self.y_true],
            y_pred_proba=aligned_reference_data[self.y_pred_proba],
            calibrator=self.calibrator,
        )

        if self.needs_calibration:
            self.calibrator.fit(
                aligned_reference_data[self.y_pred_proba],
                aligned_reference_data[self.y_true],
            )

        self.result = self._estimate(reference_data)
        self.result.data[('chunk', 'period')] = 'reference'

        return self

    def _estimate(self, data: pd.DataFrame, *args, **kwargs) -> Result:
        """Calculates the data reconstruction drift for a given data set."""
        if data.empty:
            raise InvalidArgumentsException('data contains no rows. Please provide a valid data set.')

        _list_missing([self.y_pred_proba, self.y_pred], list(data.columns))

        # We need uncalibrated data to calculate the realized performance on.
        # https://github.com/NannyML/nannyml/issues/98
        data[f'uncalibrated_{self.y_pred_proba}'] = data[self.y_pred_proba]

        if self.needs_calibration:
            data[self.y_pred_proba] = self.calibrator.calibrate(data[self.y_pred_proba])

        chunks = self.chunker.split(data)

        res = pd.DataFrame.from_records(
            [
                {
                    'key': chunk.key,
                    'chunk_index': chunk.chunk_index,
                    'start_index': chunk.start_index,
                    'end_index': chunk.end_index,
                    'start_date': chunk.start_datetime,
                    'end_date': chunk.end_datetime,
                    'period': 'analysis',
                    **self._estimate_chunk(chunk),
                }
                for chunk in chunks
            ]
        )

        multilevel_index = _create_multilevel_index(metric_names=[m.column_name for m in self.metrics])
        res.columns = multilevel_index
        res = res.reset_index(drop=True)

        if self.result is None:
            self.result = Result(
                results_data=res,
                y_pred_proba=self.y_pred_proba,
                y_pred=self.y_pred,
                y_true=self.y_true,
                timestamp_column_name=self.timestamp_column_name,
                metrics=self.metrics,
                chunker=self.chunker,
                problem_type=self.problem_type,
            )
        else:
            self.result.data = pd.concat([self.result.data, res]).reset_index(drop=True)

        return self.result

    def _estimate_chunk(self, chunk: Chunk) -> Dict:
        estimates: Dict[str, Any] = {}
        for metric in self.metrics:
            # TODO: align column naming (metric should be in front)
            estimated_metric = metric.estimate(chunk.data)
            sampling_error = metric.sampling_error(chunk.data)
            estimates[f'sampling_error_{metric.column_name}'] = sampling_error
            estimates[f'realized_{metric.column_name}'] = metric.realized_performance(chunk.data)
            estimates[f'estimated_{metric.column_name}'] = estimated_metric
            estimates[f'upper_confidence_{metric.column_name}'] = min(
                self.confidence_upper_bound, estimated_metric + SAMPLING_ERROR_RANGE * sampling_error
            )
            estimates[f'lower_confidence_{metric.column_name}'] = max(
                self.confidence_lower_bound, estimated_metric - SAMPLING_ERROR_RANGE * sampling_error
            )
            estimates[f'upper_threshold_{metric.column_name}'] = metric.upper_threshold
            estimates[f'lower_threshold_{metric.column_name}'] = metric.lower_threshold
            estimates[f'alert_{metric.column_name}'] = (
                estimated_metric > metric.upper_threshold or estimated_metric < metric.lower_threshold
            )
        return estimates
