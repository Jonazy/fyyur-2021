
def data_to_list(result):
  list_dict = []
  for i in result:
      i_dict = i._asdict()  
      list_dict.append(i_dict)
  return list_dict