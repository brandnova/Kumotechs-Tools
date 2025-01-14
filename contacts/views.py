# views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.db import IntegrityError
from .models import Contact
import json


@ensure_csrf_cookie
def manage_contacts(request):
    contacts = Contact.objects.all()
    return render(request, "single_page_contacts.html", {"contacts": contacts})

@require_http_methods(["POST"])
def create_contact(request):
    try:
        data = json.loads(request.body)
        contact = Contact.objects.create(
            prefix=data.get('prefix', ''),
            name=data.get('name'),
            email=data.get('email', ''),
            phone=data.get('phone'),
            organization=data.get('organization', ''),
            verified=False  # Explicitly set to False
        )
        return JsonResponse(contact.to_dict())
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["PUT"])
def update_contact(request, contact_id):
    try:
        data = json.loads(request.body)
        contact = get_object_or_404(Contact, id=contact_id)
        
        if data.get('update_verification_only'):
            contact.verified = data.get('verified', False)
            contact.save()
        else:
            contact.prefix = data.get('prefix', contact.prefix)
            contact.name = data.get('name', contact.name)
            contact.email = data.get('email', contact.email)
            contact.phone = data.get('phone', contact.phone)
            contact.organization = data.get('organization', contact.organization)
            contact.save()
            
        return JsonResponse(contact.to_dict())
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["DELETE"])
def delete_contact(request, contact_id):
    try:
        contact = get_object_or_404(Contact, id=contact_id)
        contact.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
@csrf_exempt
@require_http_methods(["POST"])
def public_submit_contact(request):
    try:
        data = json.loads(request.body)
        
        # Check if contact with same email or phone exists
        if Contact.objects.filter(email=data.get('email')).exists():
            return JsonResponse({'error': 'Contact with this email already exists'}, status=400)
        if Contact.objects.filter(phone=data.get('phone')).exists():
            return JsonResponse({'error': 'Contact with this phone number already exists'}, status=400)
        
        # Create new contact (verified=False by default)
        contact = Contact.objects.create(
            prefix=data.get('prefix', ''),
            name=data.get('name'),
            email=data.get('email', ''),
            phone=data.get('phone'),
            organization=data.get('organization', '')
        )
        
        return JsonResponse({
            'message': 'Contact submitted successfully. Pending verification.',
            'contact': {
                'name': contact.name,
                'email': contact.email,
                'phone': contact.phone
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def export_vcf(request):
    # Only get verified contacts
    contacts = Contact.objects.filter(verified=True)
    response = HttpResponse(content_type="text/vcard")
    response["Content-Disposition"] = "attachment; filename=contacts.vcf"

    for contact in contacts:
        # Enhanced VCF format with all fields
        vcard = [
            "BEGIN:VCARD",
            "VERSION:3.0",
            f"N:{contact.name}",
            f"FN:{contact.prefix + ' ' if contact.prefix else ''}{contact.name}",
            f"TEL:{contact.phone}",
        ]
        if contact.email:
            vcard.append(f"EMAIL:{contact.email}")
        if contact.organization:
            vcard.append(f"ORG:{contact.organization}")
        vcard.append("END:VCARD\n")
        response.write("\n".join(vcard))

    return response