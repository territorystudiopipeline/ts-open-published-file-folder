"""
Copyright (c) 2012 Shotgun Software, Inc
----------------------------------------------------

App that launches a folder browser from inside of Shotgun
"""

import tank
import sys
import os

class LaunchFolder(tank.platform.Application):
    
    def init_app(self):
        entity_types = self.get_setting("entity_types")
        deny_permissions = self.get_setting("deny_permissions")
        deny_platforms = self.get_setting("deny_platforms")
        
        p = {
            "title": "Show in File System",
            "entity_types": entity_types,
            "deny_permissions": deny_permissions,
            "deny_platforms": deny_platforms,
            "supports_multiple_selection": True
        }
        
        self.engine.register_command("show_in_filesystem", self.show_in_filesystem, p)
            
    def launch(self, path):
        self.log_debug("Launching file system viewer for folder %s" % path)        
        
        # get the setting        
        system = sys.platform
        
        # run the app
        if system == "linux2":
            cmd = 'xdg-open "%s"' % path
        elif system == "darwin":
            cmd = 'open "%s"' % path
        elif system == "win32":
            cmd = 'cmd.exe /C start "Folder" "%s"' % path
        else:
            raise Exception("Platform '%s' is not supported." % system)
        
        self.log_debug("Executing command '%s'" % cmd)
        exit_code = os.system(cmd)
        if exit_code != 0:
            self.log_error("Failed to launch '%s'!" % cmd)

    
    def show_in_filesystem(self, entity_type, entity_ids):
        paths = []
        
        for eid in entity_ids:
            # Use the path cache to look up all paths linked to the task's entity
            context = self.tank.context_from_entity(entity_type, eid)
            entity_paths = self.tank.paths_from_entity(entity_type, eid, context)
            paths.extend(entity_paths)
                    
        # More than likely the Task entity isn't represented in the filesystem
        # directly, so if we found no locations above, try the folder(s) for the
        # Task's link entity instead.
        if len(paths) == 0 and entity_type == "Task":
            filters = ["id","in"]
            filters.extend(entity_ids)
            
            tasks = self.shotgun.find("Task", [filters], ["entity"])
            for task in tasks:
                if task["entity"]:
                    context = self.tank.context_from_entity(task["entity"]["type"], task["entity"]["id"])
                    entity_paths = self.tank.paths_from_entity(task["entity"]["type"], task["entity"]["id"], context)
                    paths.extend(entity_paths)
        
        # If there's still no paths found, report an error.
        if len(paths) == 0:
            self.log_info("No location exists on disk yet for any of the selected entities. "
                        "Please use shotgun to create folders and then try again!")
            return
        
        # launch folder windows
        for x in paths:
            self.launch(x)
    
