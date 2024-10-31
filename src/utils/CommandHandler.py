class CommandHandler:
    @staticmethod
    def execute_command(command: list[str]):
        invalid_cmd: str = "Invalid command. Correct usage:"
        match command[0]:
            case "get":
                if (command.__len__() != 2):
                    raise Exception(f"{invalid_cmd} get <filename>")
            case "lap":
                if (command.__len__() != 1):
                    raise Exception(f"{invalid_cmd} lap")
            case "lpf":
                if (command.__len__() != 1):
                    raise Exception(f"{invalid_cmd} lpf")
            case "pub":
                if (command.__len__() != 2):
                    raise Exception(f"{invalid_cmd} pub <filename>")
            case "sch":
                # For this one, I'm not sure if this is going to work because it depends
                # on what the substring looks like. I might have to rethink my approach
                if (command.__len__() != 2):
                    raise Exception(f"{invalid_cmd} sch")
            case "unp":
                if (command.__len__() != 2):
                    raise Exception(f"{invalid_cmd} unp <filename>")
            case "xit":
                if (command.__len__() != 1):
                    raise Exception(f"{invalid_cmd} xit")
                CommandHandler.handle_exit()
            case _:
                raise Exception("Unknown command. Try again.")
            
    @staticmethod
    def get_command() -> list[str] | Exception:
        command_input: str = input("What would you like to do? ")
        if isinstance(command_input, str) != True:
            raise Exception("Input should be a string.")


        if (command_input.__len__() <= 0):
            raise Exception("No input given.")

        return command_input.split(" ", -1)
    
    @staticmethod
    def handle_exit():
        exit()