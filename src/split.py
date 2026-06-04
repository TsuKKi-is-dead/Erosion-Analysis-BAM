import pandas as pd
import json

df = pd.read_csv("/Users/tsukki/Downloads/files/GEE_Brahmapur/validation_points (1).csv")

df['longitude'] = df['.geo'].apply(lambda x: json.loads(x)['coordinates'][0])
df['latitude']  = df['.geo'].apply(lambda x: json.loads(x)['coordinates'][1])

df = df[['system:index', 'Predicted', 'Predicted_Class', 'longitude', 'latitude']]
df['True_Class'] = ''

df.to_csv("/Users/tsukki/Downloads/files/GEE_Brahmapur/validation_points_clean.csv", index=False)
print(f"Done: {len(df)} points")
print(df.head())