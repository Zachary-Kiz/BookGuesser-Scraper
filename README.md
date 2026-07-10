## BookGuesser Automated Book Processing Pipeline

Link to project: [BookGuesser.app](https://bookguesser.app/today)

Link to Frontend: [BookGuesser-Frontend](https://github.com/Zachary-Kiz/BookGuesser-Frontend)

Link to Backend: [BookGuesser-Backend](https://github.com/Zachary-Kiz/BookGuesserApp)

BookGuesser uses an automated AWS-based pipeline to prepare daily puzzles.

###Workflow:

1. A scheduled AWS Lambda process selects a book from the database.
2. Dockerized containers process the book cover image using OpenCV.
3. Six versions of the cover are generated with increasing levels of clarity.
4. Generated images are stored in Amazon S3.
5. Puzzle metadata is stored in PostgreSQL for retrieval by the backend API.

Technologies used:
- **Docker**
- **AWS Lambda**
- **Amazon ECR**
- **Amazon S3**
- **OpenCV**
