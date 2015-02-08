import imp
import sys

class TaskLibrary(object):

    def __init__(self, module_path, module_name, class_name, **kwargs):

        self.module_path = module_path
        self.module_name = module_name
        self.class_name = class_name

        sys.path.append(module_path)
        f, pathname, description =  imp.find_module(self.module_name)
        library_module = imp.load_module(self.module_name, f, pathname, description)
        TaskHandlerClass = getattr(library_module, self.class_name)
        self.task_handler = TaskHandlerClass(**kwargs)


    def __getattr__(self, item):
        return getattr(self.task_handler, item)


    def __getnewargs__(self):

        return (self.module_path, self.module_name, self.class_name, self.class_kwargs)


