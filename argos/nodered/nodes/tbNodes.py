from pynodered import node_red, NodeProperty


@node_red(category="argos",
          properties=dict(ProjectName=NodeProperty("Project Name", value="")
                          )
          )
def add_document(node, msg):
    msg['payload'] = str(msg['payload']).lower()
    return msg