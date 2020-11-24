from flask import current_app, flash
import pybreaker


class ReaderListener(pybreaker.CircuitBreakerListener):
    def failure(self, cb, exc):
        # flash("An unexpected error occurred. Retry later", category="error")
        pass


class LogListener(pybreaker.CircuitBreakerListener):
    "Listener used to log circuit breaker events."

    def state_change(self, cb, old_state, new_state):
        msg = "State Change: CB: {0}, New State: {1}".format(cb.name, new_state)
        current_app.logger.info(msg)

    def failure(self, cb, exc):
        current_app.logger.error(exc)


read_request_breaker = pybreaker.CircuitBreaker(
    fail_max=5, reset_timeout=30, listeners=[LogListener(), ReaderListener()]
)

write_request_breaker = pybreaker.CircuitBreaker(
    fail_max=5, reset_timeout=60, listeners=[LogListener()]
)
