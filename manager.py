import sys
import os
import json
from datetime import datetime

#configuration
File = open("config.json")
File_text = File.read()
File.close()
Configuration_json = json.loads(File_text)

Program_path = Configuration_json["program_path"]
Communication_mode = Configuration_json["communication_mode"] #text or json
Path_slash = Configuration_json["path_slash"]

# System commands
class System:
    @staticmethod
    def test():
        """test the system"""
        print("test")

    # data.json file - program settings and data (controlled by program)
    @staticmethod
    def get_data():
        """
        get data from data.json
        :return: data from data.json file in python variable
        """
        file = open(Program_path + "{slash_char}data{slash_char}data.json".format(slash_char = Path_slash), "r")
        file_text = file.read()
        file.close()
        data_json = json.loads(file_text)
        return data_json

    @staticmethod
    def update_data(data_type, value):
        """
        update one information in data.json file
        :param data_type: information (variable) name (key in file)
        :param value: new value
        """
        system_data = System.get_data()
        system_data[data_type] = value
        file = open(Program_path + "{slash_char}data{slash_char}data.json".format(slash_char = Path_slash), "w")
        file.write(json.dumps(system_data))
        file.close()

    # Project data file
    @staticmethod
    def formatid(number):
        """
        format project id (1 -> 001)
        """
        return str("{:03d}".format(number))
    @staticmethod
    def get_project_path(id):
        """
        get project path using project id
        """
        return Program_path + "{slash_char}data{slash_char}".format(slash_char = Path_slash) + System.formatid(int(id))
    @staticmethod
    def get_project_info_file(project):
        """
        get info.json file (in the project folder) using project object that only have project.path variable
        :return: project info.json as a variable
        """
        try:
            return json.loads(System.read_file(project.directory + "{slash_char}info.json".format(slash_char = Path_slash)))
        except:
            if Communication_mode != "json":
                Communication.print("Project id error")
                exit()
            return None
        #? later index file

    @staticmethod
    def update_project_info_file(project):
        """
        update info.json file (in the project folder) using project object that only have project.path variable
        """
        System.write_file(project.directory+"{slash_char}info.json".format(slash_char = Path_slash), json.dumps({ "name": project.name, "tasks": project.tasks, "tags": project.tags }))

    @staticmethod
    def update_project_folder_name(project):
        os.rename(project.directory, project.directory + "_deleted_project")

    # Settings
    @staticmethod
    def update_auth_data(login, password):
        """
        update login and password to web server in data.json file
        """
        System.update_data("login", login)
        System.update_data("password", password)

    # Files
    @staticmethod
    def write_file(directory, text):
        file = open(directory, "w")
        file.write(text)
        file.close()

    @staticmethod
    def read_file(directory):
        f = open(directory, "r")
        r = f.read()
        f.close()
        return r

    @staticmethod
    def check_directory(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    def add_file(directory, o):
        if not os.path.isfile(directory):
            f = open(directory, "w")
            f.write(json.dumps(o))
            f.close()

    # Fix files - later (it needs project index)

    def check_data_files():
        if not os.path.exists(Program_path):
            print("Błąd ścieżki programu")
            sys.exit("Error")
        System.check_directory(Program_path + "{slash_char}data".format(slash_char = Path_slash))
        System.add_file(Program_path + "{slash_char}data{slash_char}data.json".format(slash_char = Path_slash), { "last_project_id": 0, "last_task_id": 0, "login": "", "password": "" })
    """
    def fix_project(id):
        if not os.path.exists(Program_path):
            print("Błąd ścieżki programu")

        project_directory = Program_path + "{slash_char}data{slash_char}".format(slash_char = Path_slash) + System.formatid(int(id))

        project_default = json.dumps({ "name": "Project", "tasks": [], "tags": [] })
        default_values = {"name": "", "tasks": [], "tags": []}
        if not os.path.exists(project_directory + "{slash_char}info.json".format(slash_char = Path_slash)):
            #write(project_directory + "{slash_char}info.json".format(slash_char = Path_slash), project_default)
            return

        try:
            project_data = json.loads(System.read_file(project_directory + "{slash_char}info.json".format(slash_char = Path_slash)))
        except:
            System.write_file(project_directory + "{slash_char}info.json".format(slash_char = Path_slash), project_default)

        project_data = json.loads(System.read_file(project_directory + "{slash_char}info.json".format(slash_char = Path_slash)))

        for element in ["name", "tasks", "tags"]:
            try:
                test = project_data[element]
            except:
                project_data[element] = default_values[element]
                System.write_file(project_directory + "{slash_char}info.json".format(slash_char = Path_slash), json.dumps(project_data))
        """
# Check files before start - later
System.check_data_files()

# Communication manager (print json or text)
class Communication:

    @staticmethod
    def print(title, list=[], levels=2):
        """
        print information
        :param title: title of information (for example List of projects)
        :param list: table that have 1 or 2 levels (list or table)
        :param levels: number of levels
        :return:
        """
        if (Communication_mode == "json"):
            print(json.dumps({"title": title, "list": list}))
        else:
            print(title)
            for element in list:
                line = ""
                if(levels == 2):
                    # print table
                    for element2 in element:
                        line += element2 + " "
                else:
                    # print list
                    line = element + " "
                line = line[:-1]
                print(line)

   # place for sync function

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
            self.directory = Program_path + "{slash_char}data{slash_char}".format(slash_char = Path_slash)+System.formatid(self.id)
            System.check_directory(self.directory)
            System.update_data("last_project_id", self.id)

        System.update_project_info_file(self)

    def add_tag(self, tag_name):
        """add tag to the project"""

        self.tags.append(tag_name)
        self.save()
    def delete_tag(self, tag_name):
        """delete tag from the project"""

        try:
            self.tags.remove(tag_name)
            self.save()
        except:
            if(Communication_mode != "json"):
                Communication.print("Tag error")
                exit()
    def delete(self):
        """delete project"""

        System.update_project_folder_name(self)
        self.id = None #user can't save deleted project

#check projects
#projects = Project.get()
#for project in projects:
#    System.fix_project(project.id)

#Commands
if len(sys.argv) < 2:
    """program started without arguments, show list of commands"""
    commands_list = ["projects_list",
                     "projects_create (name)",
                     "projects_show (project id)",
                     "tags_create (project id) (tag name)",
                     "tags_delete (project id) (tag name)",
                     "projects_search (tag name or project name)",
                     "projects_open (project id)",
                     "projects_update (project id) (new project name)",
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
    try:
        project_name = sys.argv[2]
    except:
        Communication.print("Command syntax error")
        exit()
    project = Project()
    project.save()
    Communication.print("Created project " + project.name, [], 1)
elif sys.argv[1] == "projects_show":
    """show project"""
    try:
        project_id = int(sys.argv[2])
    except:
        Communication.print("Command syntax error")
        exit()
    print_text = []
    project = Project()
    project.find(project_id)
    print_text.append(["id:", str(project.id)])
    print_text.append(["name:", project.name])
    print_text.append(["tasks:", str(project.tasks)])
    print_text.append(["tags:", str(project.tags)])
    Communication.print("Project", print_text, 2)
elif sys.argv[1] == "tags_create":
    """add tag to project"""
    try:
        project_id = int(sys.argv[2])
        tag_name = sys.argv[3]
    except:
        Communication.print("Command syntax error")
        exit()
    project = Project()
    project.find(project_id)
    project.add_tag(tag_name)
    Communication.print("Tag added successfully!", [], 1)
elif sys.argv[1] == "tags_delete":
    """remove tag from project"""
    try:
        project_id = int(sys.argv[2])
        tag_name = sys.argv[3]
    except:
        Communication.print("Command syntax error")
        exit()
    project = Project()
    project.find(project_id)
    project.delete_tag(tag_name)
    Communication.print("Tag " + tag_name + " deleted in project " + project.name + ".")
elif sys.argv[1] == "projects_search":
    """filter projects by name and tags (search in projects)"""
    try:
        search = sys.argv[2]
    except:
        Communication.print("Command syntax error")
        exit()
    print_text = []
    all_projects_list = Project.get(search)
    for project in all_projects_list:
        print_text.append([System.formatid(project.id), project.name])
    Communication.print("Searching results", print_text, 2)
elif sys.argv[1] == "projects_open":
    """open project folder"""
    try:
        project_id = int(sys.argv[2])
    except:
        Communication.print("Command syntax error")
        exit()
    path = Program_path +  "{slash_char}data{slash_char}".format(slash_char = Path_slash) + System.formatid(project_id)
    os.startfile(path)
elif sys.argv[1] == "projects_update":
    """update project name"""
    try:
        project_id = int(sys.argv[2])
        project_name = sys.argv[3]
    except:
        Communication.print("Command syntax error")
        exit()
    project = Project()
    project.find(project_id)
    project.name = project_name
    project.save()
    Communication.print("Project " + project.name + " updated successfully")
elif sys.argv[1] == "projects_delete":
    """delete project"""
    try:
        project_id = int(sys.argv[2])
    except:
        Communication.print("Command syntax error")
        exit()
    project = Project()
    project.find(project_id)
    project.delete()
    Communication.print("Project " + project.name + " deleted successfully")
elif sys.argv[1] == "settings_authentication_update":
    """save login and password for synchronization in data.json file"""
    try:
        login = sys.argv[2]
        password = sys.argv[3]
    except:
        Communication.print("Command syntax error")
        exit()
    System.update_auth_data(login, password)
    Communication.print("Authentication data updated successfully")
else:
    Communication.print("Unknown command", [], 1) #?

