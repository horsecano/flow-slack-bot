import googletrans # pip install googletrans==4.0.0-rc1

translator = googletrans.Translator()

example = "How are you today?"
result = translator.translate(example, dest='fr')

print(f"How are you today? => {result.text}")