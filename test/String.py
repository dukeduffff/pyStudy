def test():
    content = '''**计数排序只能用在数据范围不大的场景 ** **中**** ，如果数据范围k比要排序的数据n大很多，就 ** **不**** 适合用 **
**计数**** 排序了。而且， ** **计数**** 排序只能 ** **给**** 非负整数 ** **排序****
，如果要排序的数据是其他类型的，要 ** **将**** 其在不改变相对大小的情况下'''
    content = content.replace("****", "**")
    content = content.replace("** **", "**")
    content = content.replace("**\n**", "**")
    print(content)


if __name__ == '__main__':
    test()