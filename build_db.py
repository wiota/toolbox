from portphilio_lib.models import *

def build_db():
    ## Get the user object
    mc = User.objects.get(username="maggiecasey")

    ## Drop the Media and rebuild
    Media.drop_collection()

    range_urls = [
        "https://portphilio_maggiecasey.s3.amazonaws.com/Rangeweb01.jpg",
        "https://portphilio_maggiecasey.s3.amazonaws.com/BearingTheEcho01.jpg",
        "https:///portphilio_maggiecasey.s3.amazonaws.com/Range01.jpg"]

    range_media = [Photo(owner=mc, href=x).save() for x in range_urls]

    ## Drop the Work and rebuild
    Work.drop_collection()

    range_work = Work(
        title="Range",
        slug="range",
        medium="Archival Ink Jet Print on Canvas",
        size="13' x 4'",
        date="2010",
        description="Range is a manipulated photograph taken of a military proving ground in Nevada. The resolution of the photograph was deliberately modified multiple times and layered together in a composite image. The resulting photograph appears to have multiple resolutions determined by the viewing distance.\nCollaboration between Maggie Casey and Jeffrey Stockbridge.",
        media=range_media,
        owner=mc).save()

    ins_dict_list = [
        { "title": "Gold Tooth", "slug": "gold-tooth" },
        { "title": "Processions: an Elaborative Cartography", "slug": "processions-an-elaborative-cartography" },
        { "title": "Gold Tooth; Tapestries", "slug": "gold-tooth-tapestries" },
        { "title": "Feathers", "slug": "feathers" },
        { "title": "Staircase", "slug": "staircase" },
        { "title": "Two Chairs", "slug": "two-chairs" },
        { "title": "Duck and Silkworm Celebrate Synthetic Advancement", "slug": "duck-and-silkworm-celebrate-synthetic-advancement" }]

    ins_list = [range_work] + [Work(title=x['title'], slug=x['slug'], owner=mc).save() for x in ins_dict_list]

    scu_dict_list = [
        { "title": "Breaker", "slug": "breaker" },
        { "title": "Cover", "slug": "cover" },
        { "title": "Heap", "slug": "heap" },
        { "title": "Comma", "slug": "comma" },
        { "title": "Memorial to Tray Anning", "slug": "memorial-to-tray-anning" },
        { "title": "Hers", "slug": "hers" },
        { "title": "Model: Cloud", "slug": "model-cloud" },
        { "title": "Model: Splitting", "slug": "model-splitting" },
        { "title": "Model: Hanging Angle", "slug": "model-hanging-angle" }]

    scu_list = [Work(title=x['title'], slug=x['slug'], owner=mc).save() for x in scu_dict_list]

    ## Drop the Subset and rebuild
    Subset.drop_collection()

    scu_sub = Category(subset=scu_list, slug="sculpture", title="SCULPTURE", owner=mc).save()

    ins_sub = Category(subset=ins_list, slug="installations", title="INSTALLATIONS", owner=mc).save()

    ## Drop the Body and rebuild
    Body.drop_collection()

    Body(subset=[ins_sub, scu_sub], owner=mc).save()

