import json

file_path = 'data/raw/gita_complete.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Fix 12.3 and 12.4
for shloka in data:
    if shloka['shloka_id'] == '12.3':
        shloka['hindi_meaning'] = "जो अचिन्त्य, सब जगह परिपूर्ण, अनिर्देश्य, कूटस्थ, अचल, ध्रुव, अक्षर और अव्यक्तकी उपासना करते हैं।"
    if shloka['shloka_id'] == '12.4':
        shloka['hindi_meaning'] = "।।12.4।।जो अपनी इन्द्रियोंको वशमें करके, प्राणिमात्रके हितमें रत और सब जगह समबुद्धिवाले मनुष्य मुझे ही प्राप्त होते हैं।"
    
    # Fix 12.18 and 12.19
    if shloka['shloka_id'] == '12.18':
        shloka['hindi_meaning'] = "जो शत्रु और मित्रमें तथा मान-अपमानमें सम है और शीत-उष्ण (अनुकूलता-प्रतिकूलता) तथा सुख-दुःखमें सम है एवं आसक्तिसे रहित है।"
    if shloka['shloka_id'] == '12.19':
        shloka['hindi_meaning'] = "।।12.19।।जो निन्दा-स्तुतिको समान समझनेवाला, मननशील, जिस-किसी प्रकारसे भी (शरीरका निर्वाह होनेमें) संतुष्ट, रहनेके स्थान तथा शरीरमें ममता-आसक्तिसे रहित और स्थिर बुद्धिवाला है, वह भक्तिमान् मनुष्य मुझे प्रिय है।"

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Successfully updated 12.3, 12.4, 12.18, and 12.19 in gita_complete.json")
