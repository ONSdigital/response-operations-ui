f = open("sample.csv", "a")
for i in range(5):
    f.write(f'499300{i:05}:F:50300:50300:45320:45320:8478:801325:9900000576:1:E:FE:01/09/1993:ENTNAME1_COMPANY1:'
            f'ENTNAME2_COMPANY1::RUNAME1_COMPANY1:RUNNAME2_COMPANY1::TOTAL UK ACTIVITY:::C:D:7:0001:S\n')
f.close()
