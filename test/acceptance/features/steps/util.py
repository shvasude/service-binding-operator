from command import Command

cmdObj = Command()


def search_item_from_lst(lst, srchItem):
    lst_arr = lst.split(" ")
    for item in lst_arr:
        if srchItem in item:
            if "-build" in srchItem:
                print("item matched {}".format(item))
                return item
            print("item matched {}".format(item))
            return item
    if item is None:
        print("item not matched as the value of item is {}".format(item))
        return
