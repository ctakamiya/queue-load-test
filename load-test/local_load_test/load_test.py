import json
import random
from locust import events, HttpUser, task
from locust import between
import math
import gevent

# Retrieve command line arguments
@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument("--endpoint-name", default="", help="Name of the endpoint to test")
    parser.add_argument("--databricks-pat", is_secret=True, default="", help="Databricks PAT for authentication")
    parser.add_argument("--service-rate", type=float, default=5.0, help="Service rate (requests per second)")
    parser.add_argument("--traffic-intensity", type=float, default=0.8, help="Traffic intensity (Erlang-C parameter)")
    parser.add_argument("--num-agents", type=int, default=10, help="Number of agents (c)")

class LoadTestUser(HttpUser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content_list = []  # Initialize as an empty list
        self.model_input = []

        # Read `features.json` file for model input
        try:
            with open("/local_load_test/features.json", "r") as file:
                self.content_list = file.readlines()
                print(f"Content List: {self.content_list}")
                self.model_input = [json.dumps(
                    {"messages": [{"role": "user",
                                   "content": line.strip()}]}  # Use 'line' here
                ) for line in self.content_list]  # Iterate through lines
        except FileNotFoundError:
            print("Error: features.json not found. Load test will not function correctly.")
            # Consider raising an exception or setting self.model_input to an empty list

        # Calculate arrival rate based on Erlang-C parameters
        options = self.environment.parsed_options
        self.service_rate = options.service_rate  # μ: Service rate (requests/sec per agent)
        self.traffic_intensity = options.traffic_intensity  # E: Traffic intensity
        self.num_agents = options.num_agents  # c: Number of agents

        # λ: Arrival rate = E * μ * c
        self.arrival_rate = self.traffic_intensity * self.service_rate * self.num_agents

        # Inter-arrival time follows an exponential distribution (Poisson process)
        self.inter_arrival_time = 1 / self.arrival_rate

    @task
    def query_single_model(self):
        """Simulate a user request."""
        token = self.environment.parsed_options.databricks_pat
        endpoint_name = self.environment.parsed_options.endpoint_name

        headers = {"Authorization": f"Bearer {token}"}
        
        if self.model_input:  # Check if model_input is not empty
            model_input_req = random.choice(self.model_input)
            model_input_dict = json.loads(model_input_req)
            question_content = model_input_dict['messages'][0]['content']
            print(f"Question: {question_content}")

            # Send POST request to the endpoint
            self.client.post(
                f"/serving-endpoints/{endpoint_name}/invocations",
                headers=headers,
                json=model_input_dict,
            )
            
            # Simulate Poisson arrivals by sleeping for inter-arrival time
            sleep_time = random.expovariate(self.arrival_rate)
            print(f"Sleeping for {sleep_time:.2f} seconds (Poisson inter-arrival time)")
            #self.environment.runner.spawning_greenlet.sleep(sleep_time)
            gevent.sleep(sleep_time)
        else:
            print("No model input available. Skipping task.")
