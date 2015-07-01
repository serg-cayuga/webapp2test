angular.module('webApp')
    /**
     * UserService is main service for work with auth user.
     */
    .factory('UserService', function($q, $http, $window){
        var userAuth = {};
        userAuth.user = {
            'userId': undefined,
            'fullName': undefined
        };

        userAuth.login = function(email, password){
            var deferred = $q.defer();
            $http.post('/api/login', {'email': email, 'password': password})
                .success(function(user){
                    userAuth.user.userId = user.user_id;
                    userAuth.user.fullName = user.full_name;
                    deferred.resolve(userAuth.user);
                }).error(deferred.reject);
            return deferred.promise;
        };

        userAuth.signup = function(fullName, email, password){
            var deferred = $q.defer();
            $http.post('/api/signup', {'full_name': fullName, 'email': email, 'password': password})
                .success(function(user){
                    userAuth.user.userId = user.user_id;
                    userAuth.user.fullName = user.full_name;
                    deferred.resolve(userAuth.user);
                }).error(deferred.reject);
            return deferred.promise;
        };

        userAuth.logout = function(){
            $http.get('/api/logout').success(function(){
                userAuth.user = {
                    'userId': undefined,
                    'fullName': undefined
                };
                $window.location.href = '/#/login';
            });
        };

        userAuth.getAuthUser = function(){
            var deferred = $q.defer();
            if (userAuth.user.userId === undefined){
                $http.get('/api/get-auth-user').success(function(user){
                    userAuth.user.userId = user.user_id;
                    userAuth.user.fullName = user.full_name;
                    deferred.resolve(userAuth.user);
                }).error(deferred.reject);
            }else{
                deferred.resolve(userAuth.user);
            }
            return deferred.promise;
        };

        return userAuth;
    })
    .controller('LoginController', function ($scope, $window, UserService) {
        $scope.loginData = {};
        $scope.login = function(){
            UserService.login($scope.loginData.email, $scope.loginData.password).then(function success (user){
                $window.location.href = '/#/'
            },function error(errorObj){
                $scope.loginData.error = '';
                if (typeof errorObj != 'object'){
                    $scope.loginData.error = errorObj;
                    return;
                }
                for (field in errorObj) {
                    $scope.loginData.error = field + ' error: ' + errorObj[field][0];
                }
            });
        };
    })
    .controller('SignupController', function ($scope, $window, UserService) {
        $scope.signupData = {};
        $scope.signup = function(){
            UserService.signup($scope.signupData.fullName, $scope.signupData.email, $scope.signupData.password)
                .then(function success (user){
                    $window.location.href = '/#/'
                },function error(errorObj){
                    $scope.signupData.error = '';
                    if (typeof errorObj != 'object'){
                        $scope.signupData.error = errorObj;
                        return;
                    }
                    for (field in errorObj) {
                        $scope.signupData.error = field + ' error: ' + errorObj[field][0];
                    }
                });
        };
    });