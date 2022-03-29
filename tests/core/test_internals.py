from pyttman.core.internals import PyttmanApp
from pyttman.core.decorators import LifecycleHookRepository, LifeCycleHookType
from tests.module_helper import PyttmanInternalBaseTestCase

app = PyttmanApp(client=None)


class PyttmanInternalTestPyttmanApp(PyttmanInternalBaseTestCase):

    def test_pyttman_app_lifecycle_hooks(self):
        """
        Tests that lifecycle hooks are executed by mutating the
        state of a local variable.
        """
        hook_executed = False

        @app.hooks.run("before_start")
        def something_before_start():
            nonlocal hook_executed
            hook_executed = True

        self.assertIsInstance(app.hooks, LifecycleHookRepository)
        self.assertTrue(
            callable,
            app.hooks.repository.get(LifeCycleHookType.before_start)[0])

        # Execute hooks and verify.
        app.hooks.trigger(LifeCycleHookType.before_start)
        self.assertTrue(hook_executed)
