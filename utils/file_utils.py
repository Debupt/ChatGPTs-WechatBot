from google.protobuf import text_format


def read_proto(filename, protobuf):
    with open(filename, 'r') as fp:
        return text_format.Parse(fp.read(), protobuf())
