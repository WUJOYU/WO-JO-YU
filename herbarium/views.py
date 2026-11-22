
import csv
from pathlib import PurePosixPath

from django.http import FileResponse, Http404
from django.views.decorators.cache import never_cache

from django.core.paginator import Paginator
from django.db.models import Q, Prefetch
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import (
    CollectingEvent,
    Media,
    SiteSettings,
    Specimen,
    Taxon,
    TypeDesignation,
)


# A published collecting event is not permission to disclose an unreviewed taxon.
# Hide the whole event until its associated taxon is approved (or unset).
def public_events_queryset():
    return CollectingEvent.objects.filter(is_public=True).filter(
        Q(taxon__isnull=True) | Q(taxon__publication_status='approved')
    )


def public_specimens_queryset():
    return Specimen.objects.filter(
        physically_verified=True, status__in=['verified', 'digitised'],
        collecting_event__in=public_events_queryset(),
    )


# ============================================================
# HOME
# ============================================================

def home(request):
    public_events = public_events_queryset()

    public_specimens = public_specimens_queryset()

    context = {
        'site_config': SiteSettings.objects.order_by('pk').first(),
        'event_count': public_events.count(),
        'specimen_count': public_specimens.count(),
        'digitised_count': public_specimens.filter(
            status='digitised'
        ).count(),
        'family_count': public_events.filter(
            taxon__isnull=False
        ).values('taxon__family').distinct().count(),
        'taxon_count': Taxon.objects.filter(publication_status='approved').count(),
        'recent_events': public_events.select_related(
            'taxon'
        ).order_by('-id')[:6],
    }

    return render(request, 'herbarium/home.html', context)


# ============================================================
# COLLECTING EVENTS
# ============================================================

def records(request):
    qs = public_events_queryset().select_related('taxon')

    q = request.GET.get('q', '').strip()
    family = request.GET.get('family', '').strip()

    if q:
        qs = qs.filter(
            Q(collecting_number__icontains=q) |
            Q(collector__icontains=q) |
            Q(locality__icontains=q) |
            Q(taxon__scientific_name__icontains=q) |
            Q(vernacular_name_source__icontains=q) |
            Q(taxon__family__icontains=q)
        )

    if family:
        qs = qs.filter(taxon__family=family)

    families = (
        Taxon.objects.filter(publication_status='approved').exclude(family='')
        .values_list('family', flat=True)
        .distinct()
        .order_by('family')
    )

    page_obj = Paginator(
        qs.order_by('pk'),
        25
    ).get_page(request.GET.get('page'))

    return render(request, 'herbarium/records.html', {
        'records': page_obj.object_list,
        'page_obj': page_obj,
        'q': q,
        'family': family,
        'families': families,
        'result_count': page_obj.paginator.count,
    })


def record_detail(request, pk):
    event = get_object_or_404(
        public_events_queryset().select_related('taxon'),
        pk=pk
    )

    public_specimens = event.specimens.filter(
        physically_verified=True,
        status__in=['verified', 'digitised']
    )

    return render(request, 'herbarium/record_detail.html', {
        'event': event,
        'specimens': public_specimens,
    })


# ============================================================
# SPECIMEN CATALOGUE
# ============================================================

def specimens(request):
    # Only physically verified specimens linked to public events.
    qs = public_specimens_queryset().select_related(
        'collecting_event',
        'collecting_event__taxon',
        'collecting_event__taxon__accepted_taxon'
    ).prefetch_related(Prefetch('media', queryset=Media.objects.filter(is_public=True)))

    q = request.GET.get('q', '').strip()
    family = request.GET.get('family', '').strip()
    status = request.GET.get('status', '').strip()
    images = request.GET.get('images', '').strip()
    view = request.GET.get('view', 'table').strip()
    type_filter = request.GET.get('types', '').strip()

    if view not in ('table', 'gallery'):
        view = 'table'

    # Keyword search
    if q:
        qs = qs.filter(
            Q(barcode__icontains=q) |
            Q(collecting_event__collecting_number__icontains=q) |
            Q(collecting_event__collector__icontains=q) |
            Q(collecting_event__taxon__scientific_name__icontains=q) |
            Q(collecting_event__taxon__accepted_taxon__scientific_name__icontains=q) |
            Q(collecting_event__locality__icontains=q)
        )

    # Family filter
    if family:
        qs = qs.filter(
            collecting_event__taxon__family=family
        )

    # Digitisation status
    if status in ('verified', 'digitised'):
        qs = qs.filter(status=status)

    # Public images only
    if images == 'yes':
        qs = qs.filter(
            media__is_public=True
        ).distinct()

    # Verified public type specimens only
    if type_filter == 'yes':
        qs = qs.filter(
            type_designations__verification_status='verified',
            type_designations__is_public=True
        ).distinct()

    families = (
        Taxon.objects.filter(publication_status='approved').exclude(family='')
        .values_list('family', flat=True)
        .distinct()
        .order_by('family')
    )

    # Pagination: 24 specimens per page
    page_obj = Paginator(
        qs.order_by('barcode', 'pk'),
        24
    ).get_page(request.GET.get('page'))

    return render(request, 'herbarium/specimens.html', {
        'specimens': page_obj.object_list,
        'page_obj': page_obj,
        'q': q,
        'family': family,
        'status': status,
        'images_filter': images,
        'view': view,
        'families': families,
        'result_count': page_obj.paginator.count,
        'type_filter': type_filter,
        'site_config': SiteSettings.objects.first(),
    })


# ============================================================
# SPECIMEN DETAIL
# ============================================================

def specimen_detail(request, pk):
    specimen = get_object_or_404(
        public_specimens_queryset().select_related(
            'collecting_event',
            'collecting_event__taxon',
            'collecting_event__taxon__accepted_taxon'
        ).prefetch_related(
            'media',
            'type_designations'
        ),
        pk=pk,
        physically_verified=True,
        collecting_event__is_public=True
    )

    return render(request, 'herbarium/specimen_detail.html', {
        'specimen': specimen,
        'images': specimen.media.filter(is_public=True),
        'identifications': [],  # Not public until identification-specific review exists.
        'type_designations': specimen.type_designations.filter(
            is_public=True,
            verification_status='verified'
        ),
        'site_config': SiteSettings.objects.first(),
    })


# ============================================================
# TAXONOMY
# ============================================================

def taxonomy(request):
    q = request.GET.get('q', '').strip()

    qs = Taxon.objects.filter(publication_status='approved').select_related(
        'accepted_taxon'
    ).order_by(
        'family',
        'scientific_name'
    )

    if q:
        qs = qs.filter(
            Q(scientific_name__icontains=q) |
            Q(family__icontains=q) |
            Q(vernacular_name__icontains=q)
        )

    return render(request, 'herbarium/taxonomy.html', {
        'taxa': qs[:200],
        'result_count': qs.count(),
        'q': q,
        'site_config': SiteSettings.objects.first(),
    })


# ============================================================
# DARWIN CORE EXPORT
# ============================================================

def darwin_core_export(request):
    response = HttpResponse(
        content_type='text/csv; charset=utf-8'
    )

    response['Content-Disposition'] = (
        'attachment; filename="tcf_darwin_core_event_export.csv"'
    )

    response.write('\ufeff')

    writer = csv.writer(response)

    writer.writerow([
        'eventID',
        'eventDate',
        'recordedBy',
        'recordNumber',
        'locality',
        'habitat',
        'decimalLatitude',
        'decimalLongitude',
        'minimumElevationInMeters',
        'family',
        'scientificName',
        'vernacularName',
        'institutionCode',
        'basisOfRecord',
        'occurrenceRemarks',
    ])

    events = public_events_queryset().select_related('taxon')

    for e in events.iterator():
        t = e.taxon

        writer.writerow([
            e.source_identifier,
            e.collection_date_text,
            e.collector,
            e.collecting_number,
            e.locality,
            e.habitat,
            '',
            '',
            e.elevation_m or '',
            t.family if t else '',
            t.scientific_name if t else '',
            e.vernacular_name_source,
            'TCF',
            '',
            (
                'Source collecting-event record only; '
                'physical specimen not verified. '
                f'{e.quantity_note}'
            ),
        ])

    return response


# ============================================================
# TYPE COLLECTION
# ============================================================

def type_collection(request):
    qs = TypeDesignation.objects.filter(
        is_public=True,
        verification_status='verified',
        specimen__physically_verified=True,
        specimen__collecting_event__in=public_events_queryset(),
        specimen__status__in=['verified', 'digitised']
    ).select_related(
        'specimen',
        'specimen__collecting_event'
    )

    status = request.GET.get('status', '').strip()
    q = request.GET.get('q', '').strip()

    if status in dict(TypeDesignation.TYPE_STATUSES):
        qs = qs.filter(type_status=status)

    if q:
        qs = qs.filter(
            Q(type_name__icontains=q) |
            Q(specimen__barcode__icontains=q)
        )

    return render(request, 'herbarium/type_collection.html', {
        'types': qs[:200],
        'result_count': qs.count(),
        'q': q,
        'status': status,
        'statuses': TypeDesignation.TYPE_STATUSES,
        'site_config': SiteSettings.objects.first(),
    })


@never_cache
def protected_media(request, filename):
    """Serve media only after a DB-backed public/curator permission check.

    IMPORTANT: production reverse proxies must not expose MEDIA_ROOT directly.
    """
    if not filename or "\\" in filename or "\x00" in filename:
        raise Http404
    parts = PurePosixPath(filename).parts
    if not parts or any(part in (".", "..", "") for part in parts):
        raise Http404

    staff = bool(request.user.is_authenticated and request.user.is_staff)
    file_field = None
    if filename.startswith('specimens/'):
        media = Media.objects.select_related('specimen__collecting_event__taxon').filter(
            image=filename
        ).first()
        if media is None:
            raise Http404
        specimen = media.specimen
        event = specimen.collecting_event
        allowed_public = (
            media.is_public and specimen.physically_verified
            and specimen.status in ('verified', 'digitised')
            and event.is_public
            and (event.taxon_id is None or event.taxon.publication_status == 'approved')
        )
        allowed_staff = (staff and request.user.has_perm('herbarium.view_media')
                         and request.user.has_perm('herbarium.view_specimen'))
        if not (allowed_public or allowed_staff):
            raise Http404
        file_field = media.image
    elif filename.startswith('site/'):
        site = SiteSettings.objects.filter(hero_image=filename).first()
        if site is None:
            raise Http404
        file_field = site.hero_image
    else:
        raise Http404

    try:
        return FileResponse(file_field.open('rb'), as_attachment=False)
    except (OSError, ValueError):
        raise Http404
