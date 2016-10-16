#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v2/base/task.py
"""
Task management.
"""
from __future__ import absolute_import, print_function
import functools
import logging
import traceback
from .dependency import depends
from .util import remove_if, find_if, linear as linear_fn, const
logger = logging.getLogger(__name__)

class TaskError(Exception):
    pass


KILLED = 0
RUNNING = 1
PAUSED = 2

class Task(object):

    def __init__(self, *a, **k):
        super(Task, self).__init__(*a, **k)
        self._state = RUNNING
        self._next = []
        self._task_manager = None

    def clear(self):
        pass

    def do_update(self, timer):
        pass

    def do_restart(self):
        pass

    def add_next(self, task):
        self._next.append(task)
        return task

    def update(self, timer):
        if self._state == RUNNING:
            self.do_update(timer)
        return self._state

    def pause(self):
        if self._state != KILLED:
            self._state = PAUSED
        return self

    def resume(self):
        if self._state != KILLED:
            self._state = RUNNING
        return self

    def toggle_pause(self):
        if self._state != KILLED:
            self._state = RUNNING if self._state == PAUSED else PAUSED
        return self

    def restart(self):
        self.do_restart()
        self._state = RUNNING
        if self._task_manager and self._task_manager.find(self) == None:
            manager = self._task_manager
            self._task_manager = None
            manager.add(self)
        return self

    def kill(self):
        self._state = KILLED
        if self._task_manager:
            for task in self._next:
                self._task_manager.add(task)

        return self

    @property
    def is_running(self):
        return self._state == RUNNING

    @property
    def is_paused(self):
        return self._state == PAUSED

    @property
    def is_killed(self):
        return self._state == KILLED

    @property
    def state(self):
        return self._state

    @property
    def parent_task(self):
        return self._task_manager

    def _set_parent(self, manager):
        if self._task_manager and manager:
            raise TaskError('Already attached to: ' + str(self._task_manager))
        self._task_manager = manager

    def _task_equivalent(self, other):
        return self == other


class WrapperTask(Task):

    def __init__(self, wrapped_task = None, *a, **k):
        super(WrapperTask, self).__init__(*a, **k)
        self.wrapped_task = wrapped_task

    def update(self, delta):
        super(WrapperTask, self).update(delta)
        self.wrapped_task.update(delta)

    def _set_parent(self, manager):
        super(WrapperTask, self)._set_parent(manager)
        self.wrapped_task._set_parent(manager)

    def _task_equivalent(self, other):
        return self.wrapped_task._task_equivalent(other)


class FuncTask(Task):

    def __init__(self, func = None, equivalent = None, *a, **k):
        raise func is not None or AssertionError
        super(FuncTask, self).__init__(*a, **k)
        self._func = func
        self._equivalent = equivalent

    @property
    def func(self):
        return self._orig

    @func.setter
    def func(self, func):
        self._func = func

    def do_update(self, timer):
        super(FuncTask, self).do_update(timer)
        action = self._func(timer)
        if not action or action == KILLED:
            self.kill()
        elif action == PAUSED:
            self.pause()

    def _task_equivalent(self, other):
        return self == other or self._func == other or self._equivalent == other


class GeneratorTask(Task):

    class Param(object):
        delta = 0

    def __init__(self, generator = None, equivalent = None, *a, **k):
        raise generator is not None and callable(generator) or AssertionError
        super(GeneratorTask, self).__init__(*a, **k)
        self._param = GeneratorTask.Param()
        self.generator = generator
        self._equivalent = equivalent

    @property
    def generator(self):
        return self._orig

    @generator.setter
    def generator(self, generator):
        self._orig = generator
        self._iter = generator(self._param)

    def do_update(self, delta):
        super(GeneratorTask, self).do_update(delta)
        self._param.delta = delta
        try:
            action = self._iter.next()
        except StopIteration:
            action = KILLED

        if not action or action == KILLED:
            self.kill()
        elif action == PAUSED:
            self.pause()

    def _task_equivalent(self, other):
        return self == other or self._orig == other or self._equivalent == other


class TaskGroup(Task):
    auto_kill = True
    auto_remove = True
    loop = False

    def __init__(self, tasks = [], auto_kill = None, auto_remove = None, loop = None, *a, **k):
        super(TaskGroup, self).__init__(*a, **k)
        if auto_kill is not None:
            self.auto_kill = auto_kill
        if auto_remove is not None:
            self.auto_remove = auto_remove
        if loop is not None:
            self.loop = loop
        self._tasks = []
        for task in tasks:
            self.add(task)

    def clear(self):
        for t in self._tasks:
            t._set_parent(None)

        self._tasks = []
        super(TaskGroup, self).clear()

    @depends(traceback=const(traceback))
    def do_update(self, timer, traceback = None):
        super(TaskGroup, self).do_update(timer)
        for task in self._tasks:
            if not task.is_killed:
                try:
                    task.update(timer)
                except Exception:
                    task.kill()
                    logger.error('Error when executing task')
                    traceback.print_exc()

        if self.auto_remove:
            self._tasks = remove_if(lambda t: t.is_killed, self._tasks)
        all_killed = len(filter(lambda t: t.is_killed, self._tasks)) == self.count
        if self.auto_kill and all_killed:
            self.kill()
        elif self.loop and all_killed:
            self.restart()

    def add(self, task):
        task = totask(task)
        task._set_parent(self)
        self._tasks.append(task)
        if self.is_killed:
            super(TaskGroup, self).restart()
        return task

    def remove(self, task):
        self._tasks.remove(task)
        task._set_parent(None)

    def find(self, task):
        return find_if(lambda t: t._task_equivalent(task), self._tasks)

    def restart(self):
        super(TaskGroup, self).restart()
        for x in self._tasks:
            x.restart()

    @property
    def count(self):
        return len(self._tasks)


class WaitTask(Task):
    duration = 1.0

    def __init__(self, duration = None, *a, **k):
        super(WaitTask, self).__init__(*a, **k)
        if duration is not None:
            self.duration = duration
        self.remaining = self.duration

    def do_update(self, delta):
        super(WaitTask, self).do_update(delta)
        self.remaining -= delta
        if self.remaining <= 0:
            self.kill()
            self.remaining = 0

    def do_restart(self):
        self.remaining = self.duration


class DelayTask(Task):
    duration = 1

    def __init__(self, duration = None, *a, **k):
        super(DelayTask, self).__init__(*a, **k)
        if duration is not None:
            self.duration = duration
        self.remaining = self.duration

    def do_restart(self):
        self.remaining = self.duration

    def do_update(self, delta):
        super(DelayTask, self).do_update(delta)
        self.remaining -= 1
        if self.remaining <= 0:
            self.kill()
            self.remaining = 0


class TimerTask(WaitTask):

    def do_update(self, timer):
        super(TimerTask, self).do_update(timer)
        if self.remaining == 0:
            self.on_finish()
        else:
            self.on_tick()

    def on_tick(self):
        pass

    def on_finish(self):
        pass


class FadeTask(Task):

    def __init__(self, func = lambda x: x, duration = 1.0, loop = False, init = False, *a, **k):
        super(FadeTask, self).__init__(*a, **k)
        self.func = func
        self.curr = 0.0
        self.loop = loop
        self.duration = duration
        if init:
            func(0.0)

    def do_update(self, delta):
        super(FadeTask, self).do_update(delta)
        self.func(self.curr / self.duration)
        self.curr += delta
        if self.curr >= self.duration:
            if self.loop:
                self.curr -= self.duration
            else:
                self.curr = self.duration
                self.kill()
                self.func(self.curr / self.duration)

    def do_restart(self):
        super(FadeTask, self).do_restart()
        self.curr = 0.0


class SequenceTask(Task):

    def __init__(self, tasks = [], *a, **k):
        super(SequenceTask, self).__init__(*a, **k)
        self._tasks = tasks
        self._iter = iter(tasks)
        self._current = None
        self._advance_sequence()

    def _advance_sequence(self):
        try:
            self._current = self._iter.next()
        except StopIteration:
            self.kill()

    def do_update(self, delta):
        super(SequenceTask, self).do_update(delta)
        if self._current is not None:
            self._current.update(delta)
            if self._current.is_killed:
                self._advance_sequence()

    def do_restart(self):
        for x in self._tasks:
            x.restart()

        self._iter = iter(self._tasks)
        self._advance_sequence()


def totask(task):
    if not isinstance(task, Task):
        if not callable(task):
            raise TaskError('You can add either tasks or callables. ' + str(task))
        task = FuncTask(func=task)
    return task


def generator(orig):
    equiv = [None]

    @functools.wraps(orig)
    def wrapper():
        return GeneratorTask(orig, equiv[0])

    equiv[0] = wrapper
    return wrapper


def sequence(*tasks):
    return SequenceTask(map(totask, tasks))


def parallel(*tasks):
    return TaskGroup(tasks=tasks, auto_remove=False)


def loop(*tasks):
    return TaskGroup(tasks=tasks, auto_remove=False, auto_kill=False, loop=True)


wait = WaitTask
fade = FadeTask
delay = DelayTask

def invfade(f, *a, **k):
    return fade((lambda x: f(1.0 - x)), *a, **k)


def linear(f, min, max, *a, **k):
    return fade((lambda x: f(linear_fn(min, max, x))), *a, **k)


try:
    import math

    def sinusoid(f, min = 0.0, max = 1.0, *a, **k):
        return fade((lambda x: f(min + (max - min) * math.sin(x * math.pi / 2.0))), *a, **k)


except ImportError as err:
    pass

def run(func, *a, **k):
    return FuncTask(lambda t: (None if func(*a, **k) else None))


def repeat(task):
    task = totask(task)
    task.kill = task.restart
    return WrapperTask(task)