import requests
from requests_oauthlib import OAuth1
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.modules.city.constants import TWITTER_CONSUMER_KEY, TWITTER_OAUTH_TOKEN_SECRET, TWITTER_OAUTH_TOKEN, \
    TWITTER_CONSUMER_SECRET, TWITTER_API_URL
from api.modules.city.model import City, CityImage, CityFact
from api.modules.city.serializers import CitySerializer, CityImageSerializer, CityFactSerializer


@api_view(['GET'])
def get_all_cities(request):
    """
    Returns a list of all the cities
    :param request:
    :return:
    """
    if request.method == 'GET':
        cities = City.objects.all()
        serializer = CitySerializer(cities, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def get_city(request, city_id):
    """
    Returns a city on the basis of city id
    :param request:
    :param city_id:
    :return:
    """
    try:
        city = City.objects.get(pk=city_id)
    except City.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CitySerializer(city)
        return Response(serializer.data)


@api_view(['GET'])
def get_all_city_images(request, city_id):
    """
    Returns a list of all the images for a given city id
    :param request:
    :param city_id:
    :return:
    """
    try:
        city_images = CityImage.objects.filter(city=city_id)
    except CityImage.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CityImageSerializer(city_images, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def get_all_city_facts(request, city_id):
    """
    Returns a list of all the facts for a given city id
    :param request:
    :param city_id:
    :return:
    """
    try:
        city_facts = CityFact.objects.filter(city=city_id)
    except CityFact.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CityFactSerializer(city_facts, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def get_city_trends(request, city_id):
    """
    Returns a list of top trending tweets in the given city
    :param request:
    :param city_id:
    :return:
    """
    try:
        city = City.objects.get(pk=city_id)
    except City.DoesNotExist:
        error_message = "Invalid City ID"
        return Response(error_message, status=status.HTTP_404_NOT_FOUND)

    twitter_auth = OAuth1(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_OAUTH_TOKEN,
                          TWITTER_OAUTH_TOKEN_SECRET)

    # check if city WOEID is in database or not
    if not city.woeid:
        try:
            url = TWITTER_API_URL + "closest.json?lat={0}&long={1}".format(city.latitude, city.longitude)
            woeid_response = requests.get(url, auth=twitter_auth)
            city.woeid = woeid_response.json()[0]['woeid']
            city.save()
        except Exception as e:
            return Response(str(e), status=status.HTTP_503_SERVICE_UNAVAILABLE)

    try:
        url = TWITTER_API_URL + "place.json?id={0}".format(city.woeid)
        api_response = requests.get(url, auth=twitter_auth)
        response = api_response.json()[0]['trends']
    except Exception as e:
        return Response(str(e), status=status.HTTP_503_SERVICE_UNAVAILABLE)

    return Response(response)
