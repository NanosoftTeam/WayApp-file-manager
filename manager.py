import sys
import os
import json
from datetime import datetime

#configuration
program_path = "C:\\Users\\SzymonPC\\Documents\\!Repozytoria\\WayApp_console"
communication_mode = "text"
path_slash = "" #path to manager.py file

#System commands
class System:
    #tests
    def test():
        print("test")

    #data.json
    def get_data():
        file = open(program_path + "\\data\\data.json", "r")
        file_text = file.read()
        file.close()
        data_json = json.loads(file_text)
        return data_json
    def update_data(data_type, value):
        system_data = System.get_data()
        system_data[data_type] = value
        file = open(program_path + "\\data\\data.json", "w")
        file.write(json.dumps(system_data))
        file.close()
        
    #project data
    def formatid(number):
        return str("{:03d}".format(number))
    def get_project_path(id):
        return program_path + "\\data\\" + System.formatid(int(id))
    def get_project_info_file(project):
        try:
            return json.loads(System.read_file(project.directory + "\\info.json"))
        except:
            return None
        #? later index file
    def update_project_info_file(project):
        System.write_file(project.directory+"\\info.json", json.dumps({ "name": project.name, "tasks": project.tasks, "tags": project.tags }))
    def update_project_folder_name(project):
        os.rename(project.directory, project.directory + "_deleted_project")

    #settings
    def update_auth_data(login, password):
        System.update_data("login", login)
        System.update_data("password", password)
    
    
    #files
    def write_file(directory, text):
        file = open(directory, "w")
        file.write(text)
        file.close()
    def read_file(directory):
        f = open(directory, "r")
        r = f.read()
        f.close()
        return r
    def check_directory(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
    def add_file(directory, o):
        if not os.path.isfile(directory):
            f = open(directory, "w")
            f.write(json.dumps(o))
            f.close()
    
    #fix
    def check_data_files():
        if not os.path.exists(program_path):
            print("Błąd ścieżki programu")
            sys.exit("Error")
        System.check_directory(program_path + "\\data")
        System.add_file(program_path + "\\data\\data.json", { "last_project_id": 0, "last_task_id": 0, "login": "", "password": "" })
    def fix_project(id):
        if not os.path.exists(program_path):
            print("Błąd ścieżki programu")
        
        project_directory = program_path + "\\data\\" + System.formatid(int(id))

        project_default = json.dumps({ "name": "Project", "tasks": [], "tags": [] })
        default_values = {"name": "", "tasks": [], "tags": []}
        if not os.path.exists(project_directory + "\\info.json"):
            #write(project_directory + "\\info.json", project_default)
            return
        
        try:
            project_data = json.loads(System.read_file(project_directory + "\\info.json"))
        except:
            System.write_file(project_directory + "\\info.json", project_default)
        
        project_data = json.loads(System.read_file(project_directory + "\\info.json"))

        for element in ["name", "tasks", "tags"]:
            try:
                test = project_data[element]
            except:
                project_data[element] = default_values[element]
                System.write_file(project_directory + "\\info.json", json.dumps(project_data))

# Check files before start
System.check_data_files()

#Communication manager (print json or text)
class Communication:
    def print(title, list=[], levels=2):
        if (communication_mode == "json"):
            print(json.dumps({"title": title, "list": list}))
        else:
            print(title)
            for element in list:
                line = ""
                if(levels == 2):
                    for element2 in element:
                        line += element2 + " "
                else:
                    line = element + " "
                line = line[:-1]
                print(line)
   
   #place for sync function

#CRUD models - Project
class Project:
    def __init__(self):
        """initialising project"""
        
        self.name = ""
        self.tasks = []
        self.tags = []
        self.id = None #if project id = None, project doesn't have folder yet
    def find(self, id):
        """load project from files by id"""
        
        self.directory = System.get_project_path(id)
        project_data = System.get_project_info_file(self)
        if(project_data != None):
            self.name = project_data['name']
            self.tasks = project_data['tasks'] or []
            self.tags = project_data['tags'] or []
            self.id = id
            return True
        else:
            return False
    def get(search = ""):
        """get list of project using searching"""
        
        projects = []
        last_project_id = System.get_data()["last_project_id"]
        for i in range(1, last_project_id+1):
            project = Project()
            if project.find(i):
                if((search in project.name or search in project.tags) or search == ""): #part of project name or all tag or search = 0 => get all projects
                    projects.append(project)
        return projects
    def save(self):
        """save project data in files"""
        
        if(self.id == None): #project hasn't been saved yet
            self.id = System.get_data()["last_project_id"]+1
            self.directory = program_path + "\\data\\"+System.formatid(self.id)
            System.check_directory(self.directory)
            System.update_data("last_project_id", self.id)
        
        System.update_project_info_file(self)
            
    def add_tag(self, tag_name):
        """add tag to the project"""
        
        self.tags.append(tag_name)
        self.save()
    def delete_tag(self, tag_name):
        """delete tag from the project"""
    
        self.tags.remove(tag_name)
        self.save()
    def delete(self):
        """delete project"""
        
        System.update_project_folder_name(self)
        self.id = None #user can't save deleted project
   
#CRUD models - task
"""            
class Task:
    def __init__(self, project_id, name, date=""):
        self.project_id = project_id
        self.name = name
        self.date = date
        self.saved = False
    def project_tasks(project_id):
        project = Project("")
        project.find(project_id)
        return project.tasks
    def get_all(search = ""):
        all_tasks_list = []
        last_project_id = System.get_data()["last_project_id"]
        for i in range(1, last_project_id+1):
            project = Project("")
            project.find(i)
            project.id = i
            for task in project.tasks:
                task["project_id"] = i
                if(search == "" or search in task["name"]):
                    all_tasks_list.append(task)
            
            #project_directory = program_path + "\\data\\" + System.formatid(i)
            #if os.path.exists(project_directory):
            #    project_data = json.loads(read(project_directory + "\\info.json"))
            #    project_data["id"] = i
            #    for task in project_data["tasks"]:
            #        task["project_id"] = i
            #        if(search == "" or search in task["name"]):
            #            all_tasks_list.append(task)
            
        return all_tasks_list
    def save(self):
        project = Project("")
        project.find(self.project_id)
        if(not self.saved):
            self.id = System.get_data()["last_task_id"] + 1
            project.tasks.append({"id": self.id, "name": self.name, "date": self.date})
        
        #write(self.directory+"\\info.json", json.dumps({ "name": self.name, "tasks": self.tasks, "tags": self.tags }))

        if(self.saved == True):
            for task in project["tasks"]:
                if(task["id"] == self.id):
                    task["name"] = self.name
                    task["date"] = self.date
        
        project.save()

        if(not self.saved):
            System.update_data("last_task_id", self.id)
"""

#check projects
projects = Project.get()
for project in projects:
    System.fix_project(project.id)

#Commands
if len(sys.argv) < 2:
    """program started without arguments, show list of commands"""
    commands_list = ["projects_list",
                     "projects_create (name)",
                     #"add_task projekt zadanie",
                     #"all_tasks_list",
                     #"task_list projekt",
                     "projects_show (project id)",
                     "tags_create (project id) (tag name)",
                     "tags_delete (project id) (tag name)",
                     "projects_search (project id) (tag name or project name)",
                     "projects_open (project id)",
                     "projects_update (project id) (new project name)"
                     "projects_delete (project id)",
                     "settings_authentication_update (login) (password)"]
    Communication.print("Commands", commands_list, 1)
elif sys.argv[1] == "projects_list":
    """list of projects"""
    print_text = []
    all_projects_list = Project.get()
    for project in all_projects_list:
        print_text.append([System.formatid(project.id), project.name])
    Communication.print("Projects:", print_text, 2)
elif sys.argv[1] == "projects_create":
    """create new project"""
    project = Project()
    project.name = sys.argv[2]
    project.save()
    Communication.print("Created project " + project.name, [], 1)
#elif sys.argv[1] == "add_task":
#    task_project_id = sys.argv[2]
#    task_name = sys.argv[3]
#    task_date = sys.argv[4]
#
#    task = Task(task_project_id, task_name, task_date)
#    task.save()

    #project_directory = program_path + "\\data\\" + System.formatid(int(task_project_id))
    #project_data = json.loads(read(project_directory + "\\info.json"))
    #try:
    #    project_data["tasks"].append({"id": data["last_task_id"]+1, "name": task_name, "date": task_date})
    #except:
    #    project_data.append({"tasks": []})
    #    print("Dodano")
    #    project_data["tasks"].append({"id": data["last_task_id"]+1, "name": task_name, "date": task_date})
    #write(project_directory + "\\info.json", json.dumps(project_data))
    #data["last_task_id"]+=1

    #write(program_path + "\\data\\data.json", json.dumps(data))
#    Communication.print("Dodano zadanie", [], 1)
#elif sys.argv[1] == "all_tasks_list":
#    print_text = []
#    all_tasks = Task.get_all()
#    for task in all_tasks:
#        try:
#            task_date = task["date"]
#        except:
#            task_date = "brak daty"
#        project = Project("")
#        project.find(int(task["project_id"]))
#        print_text.append([task["name"], "  (" +project.name + ", " + task_date + ")"])
        #print(task["name"] + chr(9)+ "  (" +project.name + ", " + task_date + ")")

    #for i in range(1, data["last_project_id"]+1):
    #    project_directory = program_path + "\\data\\" + System.formatid(i)
    #    project_id = System.formatid(i)
    #    if os.path.exists(project_directory):
    #        try:
    #            project_data = json.loads(read(project_directory + "\\info.json"))
    #            test = project_data["tasks"]
    #        except:
    #            project_data = json.loads(read(project_directory + "\\info.json"))
    #            project_data["tasks"] = []
    #            write(project_directory + "\\info.json", json.dumps(project_data))
    #        for task in project_data["tasks"]:
    #            try:
    #                task_date = task["date"]
    #            except:
    #                task_date = "brak daty"
    #            print(task["name"] + chr(9) +  "  (" + project_data["name"] + ", " + task_date + ")")
#    Communication.print("All tasks list:", print_text, 2)
            
#elif sys.argv[1] == "task_list":
#    print_text = []
#    project_id = sys.argv[2]
#    tasks = Task.project_tasks(project_id)
#    for task in tasks:
#        print_text.append([str(task["id"]), task["name"], " (" + task["date"] + ")"])
#    Communication.print("Tasks " + str(project_id), print_text, 2)
elif sys.argv[1] == "projects_show":
    """show project"""
    print_text = []
    project = Project()
    project.find(int(sys.argv[2]))
    print_text.append(["id:", str(project.id)])
    print_text.append(["name:", project.name])
    print_text.append(["tasks:", str(project.tasks)])
    print_text.append(["tags:", str(project.tags)])
    Communication.print("Project", print_text, 2)
elif sys.argv[1] == "tags_create":
    """add tag to project"""
    project = Project()
    project.find(int(sys.argv[2]))
    project.add_tag(sys.argv[3])
    Communication.print("Tag added successfully!", [], 1)
elif sys.argv[1] == "tags_delete":
    """remove tag from project"""
    project = Project()
    project.find(int(sys.argv[2]))
    project.delete_tag(sys.argv[3])
    Communication.print("Tag " + sys.argv[3] + " deleted in project " + project.name + ".")
elif sys.argv[1] == "projects_search":
    """filter projects by name and tags (search in projects)"""
    print_text = []
    all_projects_list = Project.get(sys.argv[2])
    for project in all_projects_list:
        print_text.append([System.formatid(project.id), project.name])
    Communication.print("Searching results", print_text, 2)
elif sys.argv[1] == "projects_open":
    """open project folder"""
    path = program_path +  "\\data\\" + System.formatid(int(sys.argv[2]))
    os.startfile(path)
elif sys.argv[1] == "projects_update":
    """update project name"""
    project = Project()
    project.find(sys.argv[2])
    project.name = sys.argv[3]
    project.save()
    Communication.print("Project " + project.name + " updated successfully")
elif sys.argv[1] == "projects_delete":
    """delete project"""
    project = Project()
    project.find(sys.argv[2])
    project.delete()
    Communication.print("Project " + project.name + " deleted successfully")
elif sys.argv[1] == "settings_authentication_update":
    """save login and password for synchronization in configuration file"""
    login = sys.argv[2]
    password = sys.argv[3]
    System.update_auth_data(login, password)
    Communication.print("Authentication data updated successfully")
else:
    Communication.print("Unknown command", [], 1) #?
