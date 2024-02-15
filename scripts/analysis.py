import pandas as pd

for i in range(3,16):
    participant = i
    condition = "Testing"
    file_path = f"data/P{participant}/p{participant}_{condition}.csv"
    data = pd.read_csv(file_path)
    
    if data.shape[0] == 420:
        data= data[data.filter(regex='^(?!Unnamed)').columns]
        data.to_csv(f"summaries/p{participant}_{condition}.csv")   
        print(f"P{i} sucessfully updated and saved") 
    else:
        li = []
        for j in range(1,421):
            try:
                df = pd.read_csv(f"data/P{participant}/p{participant}_trial_{j}_{condition}.csv")
                li.append(df)
            except:
                print(f"cant load trial {j} for participant {i}")
        frame = pd.concat(li, axis=0, ignore_index=True)
        frame.to_csv(f"summaries/p{participant}_{condition}.csv")
        print(f"P{i} df concatenated and updated")