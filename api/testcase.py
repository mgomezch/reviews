from django.test import LiveServerTestCase
from gabbi.handlers import RESPONSE_HANDLERS
from gabbi.suitemaker import test_suite_from_dict
from gabbi.reporter import ConciseTestRunner
from hypothesis.extra.django import TransactionTestCase
from io import StringIO
from unittest import defaultTestLoader


# Adapted from https://github.com/wildfish/gabbi-hypothesis-demo/blob/b4a15168895cac09342f2ae9d6b2c592332710ea/app/test_case.py  # noqa
class GabbiHypothesisTestCase(LiveServerTestCase, TransactionTestCase):
    '''
    Base test class case to handle running Gabbi tests along with Hypothesis in
    Django applications.
    '''

    def run_gabbi(self, gabbi_declaration):

        # Take only the host name and port from the live server:
        _, authority = self.live_server_url.split('://')
        host, port = authority.split(':')

        # Use Gabbi to create the test suite from our declaration:
        suite = test_suite_from_dict(
            loader=defaultTestLoader,
            test_base_name=self.id(),
            suite_dict=gabbi_declaration,
            test_directory='.',
            host=host,
            port=port,
            fixture_module=None,
            intercept=None,
            handlers=[
                handler()
                for handler in RESPONSE_HANDLERS
            ],
        )

        # Run the test.  We store the the output into a custom stream so that
        # Hypothesis can display only the simple case test result on failure
        # rather than every failing case:
        s = StringIO()
        result = ConciseTestRunner(
            stream=s,
            verbosity=0,
        ).run(suite)

        # If we weren't successful we need to fail the test case with the error
        # string from Gabbi:
        if not result.wasSuccessful():
            self.fail(
                s.getvalue(),
            )
