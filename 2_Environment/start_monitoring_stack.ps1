# Navigate to the directory containing docker-compose.yml
Set-Location -Path "C:\projects\PrometheusLocalWorkStation\2_Environment"

# Start Docker Compose services in detached mode
docker-compose -f docker-compose.yml up -d