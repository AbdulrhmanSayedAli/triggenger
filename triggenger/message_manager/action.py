from triggenger.message_manager.types import ActionPerformCallable


class Action:
    """
    A class that represents an action with a description, parameter descriptions,
    and a custom perform function.

    Attributes:
    -----------
    title : str
        A short, human-readable name for the action.
    description : str
        A brief description of the action.
    params_description : list of str
        A list of descriptions for the parameters required by the action.
    perform : ActionPerformCallable
        A function that defines the action's behavior when executed.

    Methods:
    --------
    No explicit perform method. The perform function is passed during initialization
    and is used directly.
    """

    def __init__(self, title: str, description: str, params_description: list, perform: ActionPerformCallable):
        """
        Initializes the Action instance with a custom perform function.

        Parameters:
        -----------
        title : str
            A short, human-readable name for the action.
        description : str
            A brief description of the action.
        params_description : list of str
            A list of descriptions for the parameters required by the action.
        perform : function
            A function that performs the action, accepting two arguments:
            - message: str
            - params: list
        """
        self.title = title
        self.description = description
        self.params_description = params_description
        self.perform = perform

    def display(self) -> str:
        """
        Returns a structured string that represents the action details: title, description,
        and parameter descriptions in a format that's easy for AI systems to read.

        Returns:
        --------
        str
            A formatted string containing the action's details in a readable format.
        """
        details = f"Title: {self.title}\n"
        details += f"Description: {self.description}\n"
        details += "Parameter Descriptions:\n"
        details += "[" + ",".join(self.params_description) + "]"

        return details.strip()

    def __str__(self):
        return f"Action(title='{self.title}', description='{self.description}')"

    def __repr__(self):
        return (
            f"Action(title='{self.title}', description='{self.description}', "
            f"params_description={self.params_description})"
        )
