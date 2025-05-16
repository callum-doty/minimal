FROM minio/minio:latest

# Set environment variables
ENV MINIO_ROOT_USER=minioadmin
ENV MINIO_ROOT_PASSWORD=miniopassword
# These will be overridden by the environment variables in render.yaml

# Expose the MinIO server ports
EXPOSE 9000 9001

# Command to run MinIO
CMD ["server", "/data", "--console-address", ":9001"]