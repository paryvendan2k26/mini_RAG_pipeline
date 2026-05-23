from enum import Enum


class PipelineState(Enum):
    INIT = 0
    DOCUMENTS_LOADED = 1
    DOCUMENTS_CHUNKED = 2
    INDEX_BUILT = 3
    RETRIEVAL_COMPLETE = 4
    ANSWERS_GENERATED = 5
    EVALUATION_COMPLETE = 6
    VALIDATION_COMPLETE = 7
    RESULTS_FINALISED = 8


class StateMachine:
    def __init__(self) -> None:
        self.current_state = PipelineState.INIT

    def advance(self, next_state: PipelineState) -> None:
        expected_value = self.current_state.value + 1
        if next_state.value != expected_value:
            raise ValueError(
                f"Invalid transition from {self.current_state.name} to {next_state.name}"
            )
        self.current_state = next_state

    def __str__(self) -> str:
        return self.current_state.name
