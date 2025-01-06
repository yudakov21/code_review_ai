import openai

class OpenAIClient:
    def __init__(self, openai_key: str):
        openai.api_key = openai_key

    def analyze_code(self, code_text: str, assignment: str, candidate_level: str):
        prompt = (
            f"You are an experienced code reviewer. "
            f"The following code needs to be analysed:\n{code_text}\n\n"
            f"Assignment: {assignment}\nCandidate's level: {candidate_level}\n"
            "Describe the strengths and weaknesses of the code, give a rating, and draw a conclusion."
        )

        try:
            response = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an experienced code reviewer."},
                    {"role": "user", "content": prompt},
                ], 
                max_tokens=1000,
                temperature=0.7
            )
            answer = response.choices[0].message.content
            return {
                "review": answer.strip()
            }
        except openai.OpenAIError as e:
            raise RuntimeError(f"Error OpenAI API: {str(e)}")

        
