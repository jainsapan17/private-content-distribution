import aws_cdk as core
import aws_cdk.assertions as assertions

from myapp_cdk.myapp_cdk_stack import MyappCdkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in myapp_cdk/myapp_cdk_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = MyappCdkStack(app, "myapp-cdk")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
