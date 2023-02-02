import importlib
import os
import rapidjson as json
from dataclasses import dataclass, asdict
from typing import Optional

from dacite import from_dict, MissingValueError, WrongTypeError

from zigbeeLauncher import base_dir
from zigbeeLauncher.auto_scripts import capacity, stability, State, Status, Result, ScriptName
from zigbeeLauncher.auto_scripts.script import Script
from zigbeeLauncher.logging import autoLogger as logger


@dataclass
class Config:
    capacity: Optional[capacity.Config]
    stability: Optional[stability.Config]


class Testing(Script):
    def __init__(self, status_callback):
        self.tests = {}
        super().__init__(script=ScriptName.COMPOSE, path=os.path.join(base_dir, 'scripts/'+ScriptName.COMPOSE+'.json'),
                         status_callback=status_callback)
        status_callback(State.READY, Status.INFO)

    def _instantiation(self, script, config):
        if script not in self.tests:
            # update config
            with open(os.path.join(base_dir, 'scripts/' + script + '.json'), 'w',
                      encoding='utf-8') as f:
                f.write(json.dumps(config, indent=4))
            # instantiation capacity
            testing = importlib.import_module('zigbeeLauncher.auto_scripts.' + script)
            test = testing.Testing(self.update_callback)

            # update record
            test.set_record(self.record)

            self.tests[script] = test
            return test.ready
        else:
            test = self.tests[script]
            test.set_config(config)
        if not test.ready:
            self.log(Status.ERROR, test.error)
            return False
        else:
            return True

    def load_config(self):
        self.ready = False
        self.tests.clear()
        if not self.config:
            logger.error("Cannot get config")
            self.update(State.FINISH, Result.STOP)
        else:
            if self.config.get(ScriptName.CAPACITY):
                if not self._instantiation(ScriptName.CAPACITY,
                                           self.config.get(ScriptName.CAPACITY)):
                    return
            if self.config.get(ScriptName.STABILITY):
                if not self._instantiation(ScriptName.STABILITY,
                                           self.config.get(ScriptName.STABILITY)):
                    return
            self.ready = True

    def start(self):
        self.update(State.START, Result.SUCCESS)
        if not self.tests:
            logger.error("no valid test object")
            self.log(Status.ERROR, "no valid test object")
            self.update(State.FINISH, Result.STOP)
            return
        self.running = True
        self.update(State.WORKING, Result.SUCCESS)
        for script, test in self.tests.items():
            self.log(Status.INFO, f"starting {script}")
            test.start()
            if test.state == State.FINISH:
                if test.result == Result.SUCCESS:
                    self.log(Status.INFO, f"{script} done")
                else:
                    self.log(Status.ERROR, f"{script} exit error")
                    return
        self.update(State.FINISH, Result.SUCCESS)
        self.running = False

    def stop(self):
        self.running = False
        for script, test in self.tests.items():
            if test.running:
                test.stop()

        self.tests.clear()

    def update_result(self, status, descriptor):
        pass

    def preparing(self):
        pass

    def working(self):
        pass