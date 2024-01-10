import os
import re
import subprocess
import json
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def findomain_view(request):
    # Get the current timestamp in milliseconds
    if request.method == 'POST':
        try:
            request_data = json.loads(request.body)
            domain = request_data.get('domain')
            options = request_data.get('options')
            user = request_data.get('user')
            
            if not domain:
                return JsonResponse({'error': 'Missing domain'}, status=400)

            command = ['subfinder', '-d', domain]

            if options:
                options_list = options.split(',')
                command.extend(options_list)

            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            user_folder = os.path.join('C:\subdomain', user)  
            if not os.path.exists(user_folder):
                # Create the user's folder if it doesn't exist
                os.makedirs(user_folder)

            # Generate the timestamp folder and output.json file
            timestamp = str(time.time()*1000)
            timestamp_folder = os.path.join(user_folder, timestamp)
            os.makedirs(timestamp_folder)
            output_file = os.path.join(timestamp_folder, 'output.json')
            if process.returncode != 0:
                return JsonResponse({'error': error.decode()}, status=400)

            results = output.decode().split('\n')
            results = [item.strip() for item in results]

            subdomains = []
            ip_addresses = []
            res=[]
            for result in results:
                result = result.strip()
                if not result:
                    continue

                match = re.match(r'([^,]+),\s?(\d+\.\d+\.\d+\.\d+)', result)
                if match:
                    subdomain = match.group(1)
                    ip_address = match.group(2)
                    subdomains.append(subdomain)
                    ip_addresses.append(ip_address)
                else:
                    subdomain=results
            response_data = {
                'subdomains': subdomains,
                'ip_addresses': ip_addresses
            }
            response={
                'subdomains':results
            }
            if not subdomains:
                with open(output_file, 'w') as f:
                    json.dump(response, f)
                    return JsonResponse(response, status=200)
            else:
                with open(output_file, 'w') as f:
                    json.dump(response_data,f)
                    return JsonResponse(response_data, status=200)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
