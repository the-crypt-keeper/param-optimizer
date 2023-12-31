import random

class ParameterMutation:
    def __init__(self, parameter, value, mutation_type, mutation_value, max_value=None, min_value=None):
        """
        A class representing a single mutable parameter.

        Args:
            parameter (str): The name of the parameter.
            value (int or float): The initial value of the parameter.
            mutation_type (str): The type of mutation to apply (either 'additive' or 'geometric').
            mutation_value (dict): The value used for mutation, which can be either a constant or a range.
                - If constant: {'constant': value}
                - If range: {'uniform': (min_value, max_value)}
            max_value (int or float, optional): The maximum value allowed for the parameter. Defaults to None.
            min_value (int or float, optional): The minimum value allowed for the parameter. Defaults to None.
        """
        self.parameter = parameter
        self.value = value
        self.mutation_type = mutation_type
        self.mutation_value = mutation_value
        self.min_value = min_value
        self.max_value = max_value

    def gen_value(self):
        """
        Applies mutation to generation and return a potential new value.
        """
        if 'uniform' in self.mutation_value:
            v = random.uniform(*self.mutation_value['uniform'])
        elif 'constant' in self.mutation_value:
            v = self.mutation_value['constant']
        if self.min_value is not None and v < self.min_value:
            v = self.min_value
        elif self.max_value is not None and v > self.max_value:
            v = self.max_value
        return v

    def mutate(self):
        """
        Applies mutation to the parameter based on the mutation type.

        If mutation_type is 'additive', the parameter value is increased by the generated value.
        If mutation_type is 'geometric', the parameter value is multiplied by the generated value.
        """
        if self.mutation_type == 'additive':
            self.value += self.gen_value()
        elif self.mutation_type == 'geometric':
            self.value *= self.gen_value()

    def __repr__(self):
        """
        Returns a string representation of the ParameterMutation object.
        """
        value_str = f'{self.value}' if isinstance(self.value, int) else f'{self.value:.3f}'
        return f'{self.parameter}: {value_str}'

class ParameterMutationList:
    def __init__(self, params, id, parent=[], values={}):
        """
        A class representing a set of mutable parameters.

        Args:
            params (list): A list of dictionaries representing the parameters and their mutation configurations.
            id (int): The identifier for the ParameterMutationList instance.
            parent (list, optional): A list of parent IDs. Defaults to an empty list.
        """
        self.id = id
        self.parent = parent
        self.mutation_list = [ParameterMutation(**mutation_dict) for mutation_dict in params]

        for mutation in self.mutation_list:
            if values.get(mutation.parameter):
                mutation.value = values[mutation.parameter]

    def get_parameters(self):
        """
        Retrieves the current values of all parameters in a dictionary format.
        """
        return {mutation.parameter: mutation.value for mutation in self.mutation_list}

    def clone(self, new_id):
        """
        Creates a clone of the ParameterMutationList instance with a new ID.

        Args:
            new_id (int): The identifier for the cloned instance.

        Returns: The cloned instance of the ParameterMutationList class.
        """
        return ParameterMutationList([mutation.__dict__ for mutation in self.mutation_list], new_id, [self.id])

    def mutate(self, new_id, iter):
        """
        Generates a mutated version of the ParameterMutationList instance.

        Args:
            new_id (int): The identifier for the mutated instance.
            iter (int): The number of mutations to apply.

        Returns: The mutated instance of the ParameterMutationList class.
        """
        mutant = self.clone(new_id)
        for _ in range(iter):
            mutation = random.choice(mutant.mutation_list)
            mutation.mutate()
        return mutant

    def breed(self, new_id, other):
        """
        Creates a child ParameterMutationList instance by breeding with another instance.

        Args:
            new_id (int): The identifier for the child instance.
            other (ParameterMutationList): The other instance to breed with.

        Returns: The child instance resulting from breeding.
        """
        child = self.clone(new_id)
        child.parent = [self.id, other.id]
        other_params = other.get_parameters()
        for mutation in child.mutation_list:
            mutation.value = random.choice([mutation.value, other_params[mutation.parameter]])
        return child

    def __repr__(self):
        """
        Returns a string representation of the ParameterMutationList object.
        """
        return f"[{self.id:2d} | {self.parent}] " + ' '.join([str(mutation) for mutation in self.mutation_list])
    