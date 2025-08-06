#!/usr/bin/env python
import os
import sys
import argparse


class TestRunner:
    """Custom test runner class to handle test command with coverage options."""

    def __init__(self):
        self.parser = argparse.ArgumentParser(add_help=False)
        self.parser.add_argument(
            "--with-coverage",
            action="store_true",
            help="Run tests with coverage report",
        )
        self.parser.add_argument(
            "--html", action="store_true", help="Generate HTML coverage report"
        )
        self.parser.add_argument(
            "--xml", action="store_true", help="Generate XML coverage report"
        )
        self.parser.add_argument(
            "--output-dir",
            default="coverage_reports",
            help="Output directory for coverage reports",
        )

    def run_tests(self, args):
        # Check if we're trying to run tests with our custom options
        if len(args) > 1 and args[1] == "test":
            try:
                # Parse only our custom arguments
                test_args_start = args.index("test") + 1
                test_args = args[test_args_start:]

                # Parse known args to extract coverage-related options
                options, remaining = self.parser.parse_known_args(test_args)

                if options.with_coverage:
                    try:
                        # Import coverage here to avoid dependency if not used
                        import coverage
                        import pytest

                        # Setup coverage
                        cov = coverage.Coverage()
                        cov.start()

                        # Build pytest arguments
                        pytest_args = ["--reuse-db"]

                        # Run tests with pytest
                        print("Running tests with coverage...")
                        result = pytest.main(pytest_args + remaining)

                        # Stop and save coverage
                        cov.stop()
                        cov.save()

                        # Generate reports based on options
                        if options.html:
                            os.makedirs(options.output_dir, exist_ok=True)
                            html_dir = os.path.join(options.output_dir, "html")
                            print(f"Generating HTML coverage report in {html_dir}")
                            cov.html_report(directory=html_dir)

                        if options.xml:
                            os.makedirs(options.output_dir, exist_ok=True)
                            xml_path = os.path.join(options.output_dir, "coverage.xml")
                            print(f"Generating XML coverage report: {xml_path}")
                            cov.xml_report(outfile=xml_path)

                        # Always print coverage report to console
                        print("Coverage summary:")
                        cov.report()

                        # Return pytest exit code
                        return result
                    except ImportError as e:
                        print(f"Error: {e}")
                        print("Make sure pytest and coverage are installed:")
                        print("pip install pytest pytest-django coverage")
                        return 1

            except ValueError:
                # 'test' not found or other parsing error, continue with Django's default runner
                pass

        # Fall back to Django's default test runner
        from django.core.management import execute_from_command_line

        return execute_from_command_line(args)


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ft.settings")
    try:
        # Use our custom test runner
        runner = TestRunner()
        sys.exit(runner.run_tests(sys.argv))
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions.
        try:
            import django  # noqa: F401
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
