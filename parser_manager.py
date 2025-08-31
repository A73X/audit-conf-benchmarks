import os, importlib, inspect

class ParserManager:
    def __init__(self):
        self.parsers_paths_l = []
        self.parsers_l = []
        self.__list_parsers()
        self.__load_parsers()
    
    def __list_parsers(self):
        parsers_paths_l = []
        for root, dirs, files in os.walk("./PARSERS/"):
            for file in files:
                file_path = os.path.join(root, file)
                # Exclude __pycache__ files
                if "__pycache__" not in file_path:
                    parsers_paths_l.append(file_path)
        self.parsers_paths_l = parsers_paths_l
    
    def __load_parsers(self):
        parsers_l = []
        for parser_path in self.parsers_paths_l:
            try:
                # Create module name from file path
                module_name = os.path.splitext(os.path.basename(parser_path))[0]

                # Load module from file path
                spec = importlib.util.spec_from_file_location(module_name, parser_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find all classes in the module
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # Skip imported classes (only get classes defined in this module)
                    if obj.__module__ == module_name:
                        try:
                            # Instantiate the class
                            parser_instance = obj()
                            parsers_l.append(parser_instance)
                        except Exception as e:
                            print(f"Failed to instantiate parser {name}: {e}")
                            
            except Exception as e:
                print(f"Failed to load module from {parser_path}: {e}")
        self.parsers_l = parsers_l

    def parse(self, file, regkeys_l):
        for parser in self.parsers_l:
            for parsable_file in parser.parsable_files_l:
                if parsable_file in file:
                    found_values_d, found_proofs_d  = parser.parse(file, regkeys_l)
                    return found_values_d, found_proofs_d
                