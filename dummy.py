import regex as re

string = ["abcdefg",]

string2 = string.copy()
string2[0] = re.sub("d", "D", string2[0])

print(string, string2)