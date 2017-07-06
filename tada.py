class MyWorksheet:
    def __init__(self, nameofsheet="Page 1", encoding='utf-8'):
        self.wb = xlwt.Workbook(encoding=encoding)
        self.ws = self.wb.add_sheet(nameofsheet)
        self.li = itertools.count(0)
    
    def write_line(self, *objects):
        i = next(self.li)
        for j,x in enumerate(objects):
            self.ws.write(i, j, x)

xl = MyWorksheet("A test Sheet")

xl.write_line("date", "checkpoint id", "checkpoint name", "vote", "option")
for vote_pb in vote_pbs:
    if vote_pb.checkpoint_id in checkpoint_ids_to_names:
        xl.write_line(
            vote_pb.locale_datetime,
            vote_pb.checkpoint_id,
            checkpoint_ids_to_names[vote_pb.checkpoint_id],
            chart_utils.AnswerEnumFriendly(vote_pb.value),
            vote_pb.qcm_slug
        )
    
wb.save('aatestxl.xls')
f = open('aatestxl.xls','r')
xlsFile=f.read()
# print(json.dumps(xlsFile))
# return json.dumps(out)