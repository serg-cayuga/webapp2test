var webApp = angular.module('webApp', ['ngRoute', 'ngResource']);

webApp
    .config(function ($routeProvider, $httpProvider) {
        $routeProvider
            .when('/', {
                templateUrl: '/static/templates/dashboard.html',
                controller: 'MainController',
                resolve: {
                    /**
                     * Resolving this param ensures that only Logged in user has access for the route.
                     */
                    'authUser': function(UserService){
                        return UserService.getAuthUser();
                    }
                }
            })
            .when('/login', {
                templateUrl: '/static/templates/login.html',
                controller: 'LoginController'
            })
            .when('/signup', {
                templateUrl: '/static/templates/signup.html',
                controller: 'SignupController'
            })
            .otherwise({
                redirectTo: '/'
            });

        /**
         * Redirect to login page if any Unauthorized response is got.
         */
        $httpProvider.interceptors.push(function($q, $window) {
            return {
               'responseError': function handleUnauthorizedExeption(rejection) {
                  if (rejection.status == 401) {
                      $window.location.href = '/#/login';
                      return $q.reject(rejection);
                  }
                  return $q.reject(rejection);
               }
            };
        });
    })
    .factory('UserResource', function ($resource) {
        return $resource('/api/users/:id', {}, {});
    })
    .factory('MessagesResource', function ($resource) {
        return $resource('/api/users/:id/messages', {id:'@id'}, {
            'send': {method: 'POST'}
        });
    });