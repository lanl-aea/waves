"""Module of package specific exceptions.

The project design intent is to print error messages to STDERR and return non-zero exit codes when used as a command
line utility (CLI), but raise exceptions when used as a package (API). The only time a stack trace should be printed
when using the CLI is if the exception is unexpected and may represent an internal bug.

Most raised exceptions in the package API should be Python built-ins. However, to support the CLI error handling
described above some exceptions need to be uniquely identifiable as package exceptions and not third-party exceptions.
:meth:`waves.exceptions.WAVESError` and ``RuntimeError`` exceptions will be be caught by the command line utility and
converted to error messages and non-zero return codes. Third-party exceptions represent truly unexpected behavior that
may be an internal bug and print a stack trace.

This behavior could be supported by limiting package raised exceptions to RuntimeError exceptions; however, more
specific exceptions are desirable when using the package API to allow end-users to handle different collections of API
exceptions differently.
"""


class WAVESError(Exception):
    """The base class for WAVES exceptions. All exceptions that must be caught by the CLI should derive from this
    class.
    """


class APIError(WAVESError):
    """Raised when an API validation fails, e.g. an argument value is outside the list of acceptable choices. Intended
    to mirror an associated ``argparse`` CLI option validation."""


class MutuallyExclusiveError(APIError):
    """Raised during API validation that mirrors an ``argparse`` CLI mutually exclusive group."""


class ChoicesError(APIError):
    """Raised during API validation that mirrors an ``argparse`` CLI argument with limited choices."""


class SchemaValidationError(APIError):
    """Raised when a WAVES parameter generator schema validation fails"""
