word_list=input("Enter words separated by spaces: ").split()
print(word_list)
ovel_list=['a','e','i','o','u','A','E','I','O','U']
word_dict={}
for word in word_list:
    count=0
    for char in word:
        if char in ovel_list:
            count+=1
    word_dict[word]=count
print("================================")
print("Word Dictionary:", word_dict)
print("================================")