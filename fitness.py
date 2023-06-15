class FitnessBase():
    def get_evaluation(self, params):
        print("FitnessBase: get_evaluation", params)
        return None, None
    
    def perform_evaluation(self, params):
        print("FitnessBase: perform_evaluation", params)
        pass

    def wait_all(self):
        print("FitnessBase: wait_all")
        pass