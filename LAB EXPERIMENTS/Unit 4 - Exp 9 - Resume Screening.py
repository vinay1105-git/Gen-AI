from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")
job = input("Enter the engineering job description: ")

n = int(input("Enter number of resumes: "))
resumes = [input(f"Enter resume {i + 1}: ") for i in range(n)]

job_embedding = model.encode(job, convert_to_tensor=True)
scores = []

for i, resume in enumerate(resumes):
    resume_embedding = model.encode(resume, convert_to_tensor=True)
    score = util.cos_sim(job_embedding, resume_embedding).item()
    scores.append((i + 1, score))

scores.sort(key=lambda x: x[1], reverse=True)

print("\nResume Ranking:")
for rank, (resume_no, score) in enumerate(scores, 1):
    print(f"{rank}. Resume {resume_no} - Score: {score:.4f}")
