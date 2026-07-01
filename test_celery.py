from app.tasks import add

result = add.delay(10, 20)

print("Task ID:", result.id)
print("Result:", result.get())