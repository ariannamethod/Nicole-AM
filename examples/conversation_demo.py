from Nicole.models.conversation import get_conv_template

if __name__ == "__main__":
    conv = get_conv_template("nicole")
    conv.append_message(conv.roles[0], "Hello Nicole, who are you?")
    conv.append_message(conv.roles[1], None)
    print(conv.get_prompt())
