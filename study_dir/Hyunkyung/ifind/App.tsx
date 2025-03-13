import AsyncStorage from '@react-native-async-storage/async-storage';
import messaging from '@react-native-firebase/messaging';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useEffect, useState } from 'react';
import { enableLatestRenderer } from 'react-native-maps';
import PushNotification from 'react-native-push-notification';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import BottomTabNavigation from './src/navigation/BottomTabNavigation';
import { LoginPage } from './src/screens/LoginPage';
import { SignupPage } from './src/screens/SignupPage';


enableLatestRenderer();

const Stack = createNativeStackNavigator();


export default function App() {

  const [isUserLoggedIn, setIsUserLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkLoginStatus = async () => {
      try {
        const uid = await AsyncStorage.getItem('userUID');
        setIsUserLoggedIn(uid !== null);
        setIsLoading(false);
      } catch (e) {
        console.error(e);
        setIsLoading(false);
      }
    };

    checkLoginStatus();
  }, []);

  if (isLoading) {
    return null;
  }

  PushNotification.createChannel(
    {
      channelId: "아이파인", // 채널 ID
      channelName: "아이파인", // 채널 이름
      channelDescription: "", // 채널 설명
      soundName: "default", // 기본 사운드 사용
      importance: 4, // 중요도 설정
      vibrate: true, // 진동 여부
    },
    (created: boolean) => console.log(`CreateChannel returned '${created}'`) // 콜백 함수
  );

  messaging().onMessage(async remoteMessage => {
    PushNotification.localNotification({
      channelId: "아이파인",
      title: remoteMessage.notification?.title ?? '아이파인', // 알림 제목
      message: remoteMessage.notification?.body ?? '도착했습니다',// 알림 내용
      // bigText: remoteMessage.notification? body ?? 'Default big text',
      subText: "", // 서브 텍스트
      priority: "high", // 우선순위
      importance: "high", // 중요도
      soundName: "default", // 사운드 이름
    });
  });
  messaging().setBackgroundMessageHandler(async remoteMessage => {
    PushNotification.localNotification({
      channelId: "아이파인",
      title: remoteMessage.notification?.title ?? '아이파인', // 알림 제목
      message: remoteMessage.notification?.body ?? '도착했습니다',// 알림 내용
      // bigText: remoteMessage.notification? body ?? 'Default big text',
      subText: "", // 서브 텍스트
      priority: "high", // 우선순위
      importance: "high", // 중요도
      soundName: "default", // 사운드 이름
    });
  });

  return (
    <SafeAreaProvider>
      <NavigationContainer>
      <Stack.Navigator
        screenOptions={{ headerShown: false }}
        initialRouteName={isUserLoggedIn ? "MainPage" : "LoginPage"}
      >
        {/* 로그인 여부와 상관없이 모든 스크린을 렌더링합니다. */}
        <Stack.Screen name="MainPage" component={BottomTabNavigation} />
        <Stack.Screen name="LoginPage" component={LoginPage} />
        <Stack.Screen name="SignupPage" component={SignupPage} />
      </Stack.Navigator>
      </NavigationContainer>

    </SafeAreaProvider>
  );
}
