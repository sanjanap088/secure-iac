from flask import Flask, request

from templateGeneration.builder import MyAwsStackBuilder

app = Flask(__name__)
awsBuilder = MyAwsStackBuilder()

STACK_NAME = 'stackName'
PROVIDER = 'provider'
RESOURCE_BENCHMARK_MAP = 'resourceBenchmarkMap'
AWS = 'aws'
AZURE = 'azure'


@app.route('/tfstack', methods=['POST'])
def generateTerraformJson():
    print("in controller")
    # request body as dictionary
    req_json = request.json

    if STACK_NAME not in req_json:
        return f"Bad request - {STACK_NAME} not present", 400

    stack_name = req_json[STACK_NAME]

    if PROVIDER not in req_json:
        return f"Bad request - {PROVIDER} not present", 400

    provider = req_json[PROVIDER]

    if RESOURCE_BENCHMARK_MAP not in req_json:
        return f"Bad request - {RESOURCE_BENCHMARK_MAP} not present", 400

    resource_benchmark_map = req_json[RESOURCE_BENCHMARK_MAP]

    if provider == AWS:
        return awsBuilder.get_terraform_stack_json(stack_name, resource_benchmark_map)

    if provider == AZURE:
        return {"message": "Terraform stack json for Azure"}

    return "Unknown provider", 400


if __name__ == '__main__':
    app.run()
