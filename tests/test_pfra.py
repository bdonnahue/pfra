from unittest import TestCase
from ShellUtilities import Shell
from ShellUtilities.ShellCommandException import ShellCommandException
import os

class Test_pfra(TestCase):

    def __init__(self, *args, **kwargs):
        super(Test_pfra, self).__init__(*args, **kwargs)

        self.mock_service_name = "MockService"

        # Set the environment variables as if we configured the resource agent using pcs
        self.env = os.environ
        self.env["OCF_ROOT"] = "/usr/lib/ocf/"
        self.env["OCF_RESKEY_service_name"] = self.mock_service_name
        self.env["OCF_RESKEY_promote_script"] = ""
        self.env["OCF_RESKEY_demote_script"] = ""

        # Determine the current directory
        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.root_dir = os.path.dirname(current_dir)

        # Determine the path to the shell script
        self.shell_script_path = os.path.join(self.root_dir, "src", "pfra.sh")

    def __is_service_running(self):

        shell_command = "systemctl status {0} | grep -E '^   Active: active \(running\)'".format(self.mock_service_name)
        try:
            shell_command_results = Shell.execute_shell_command(shell_command)
            return True
        except ShellCommandException:
            return False

    def __stop_mock_service(self):
        Shell.execute_shell_command("systemctl stop {0}".format(self.mock_service_name))

    def __start_mock_service(self):
        Shell.execute_shell_command("systemctl start {0}".format(self.mock_service_name))

    def test__usage__success__called_by_name(self):
        if self.__is_service_running():
            self.__stop_mock_service()

        try:
            shell_command = "bash {0} usage".format(self.shell_script_path)
            shell_command_results = Shell.execute_shell_command(shell_command, env=self.env)
        except ShellCommandException as scex:
            self.assertEqual(2, scex.ExitCode)
            self.assertTrue("start|stop|monitor|meta-data|promote|demote" in scex.Stdout)
            self.assertEqual("", scex.Stderr)
            self.assertFalse(self.__is_service_running())

        if self.__is_service_running():
            self.__stop_mock_service()

    def test__usage__success__no_args_supplied(self):
        if self.__is_service_running():
            self.__stop_mock_service()

        try:
            shell_command = "bash {0}".format(self.shell_script_path)
            shell_command_results = Shell.execute_shell_command(shell_command, env=self.env)
        except ShellCommandException as scex:
            self.assertEqual(2, scex.ExitCode)
            self.assertTrue("start|stop|monitor|meta-data|promote|demote" in scex.Stdout)
            self.assertEqual("", scex.Stderr)
            self.assertFalse(self.__is_service_running())

        if self.__is_service_running():
            self.__stop_mock_service()

    def test__start__success__not_started(self):

        if self.__is_service_running():
            self.__stop_mock_service()

        shell_command = "bash {0} start".format(self.shell_script_path)
        shell_command_results = Shell.execute_shell_command(shell_command, env=self.env)
        self.assertEqual(0, shell_command_results.ExitCode)
        self.assertTrue("Starting the service succeeded" in shell_command_results.Stderr)
        self.assertTrue(self.__is_service_running())

        if self.__is_service_running():
            self.__stop_mock_service()

    def test__start__success__already_started(self):

        if self.__is_service_running():
            self.__stop_mock_service()

        shell_command = "bash {0} start".format(self.shell_script_path)
        shell_command_results = Shell.execute_shell_command(shell_command, env=self.env)
        self.assertEqual(0, shell_command_results.ExitCode)
        self.assertTrue("Starting the service succeeded" in shell_command_results.Stderr)
        self.assertTrue(self.__is_service_running())

        shell_command_results = Shell.execute_shell_command(shell_command, env=self.env)
        self.assertEqual(0, shell_command_results.ExitCode)
        self.assertTrue("Starting the service succeeded" in shell_command_results.Stderr)
        self.assertTrue(self.__is_service_running())

        if self.__is_service_running():
            self.__stop_mock_service()

    def test__stop__success__not_started(self):

        if self.__is_service_running():
            self.__stop_mock_service()

        shell_command = "bash {0} stop".format(self.shell_script_path)
        shell_command_results = Shell.execute_shell_command(shell_command, env=self.env)
        self.assertEqual(0, shell_command_results.ExitCode)
        self.assertTrue("Stopping the service succeeded" in shell_command_results.Stderr)
        self.assertTrue(self.__is_service_running())

        if self.__is_service_running():
            self.__stop_mock_service()

    def test__stop__success__already_started(self):

        if not self.__is_service_running():
            self.__start_mock_service()

        shell_command = "bash {0} stop".format(self.shell_script_path)
        shell_command_results = Shell.execute_shell_command(shell_command, env=self.env)
        self.assertEqual(0, shell_command_results.ExitCode)
        self.assertTrue("Stopping the service succeeded" in shell_command_results.Stderr)
        self.assertTrue(self.__is_service_running())

        shell_command_results = Shell.execute_shell_command(shell_command, env=self.env)
        self.assertEqual(0, shell_command_results.ExitCode)
        self.assertTrue("Starting the service succeeded" in shell_command_results.Stderr)
        self.assertTrue(self.__is_service_running())

        if self.__is_service_running():
            self.__stop_mock_service()
