import { BottomTabBar, BottomTabBarProps, createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import React from 'react';
import { Image, SafeAreaView, StyleSheet } from 'react-native';
import { GroupPage } from '../screens/GroupPage';
import { MakeGroup } from '../screens/MakeGroup';
import { QRPage } from '../screens/QRPage';
import { SettingPage } from '../screens/Settingpage';
import { UploadPage } from '../screens/UploadPage';
import theme from '../styles/theme';
const Tab = createBottomTabNavigator();

const colorchange = theme.navicolor;

const BottomTabNavigation = () => {
    return (
            <Tab.Navigator
                tabBar={(props: BottomTabBarProps) => (
                    <SafeAreaView style={styles.container}>
                        <BottomTabBar {...props} />
                    </SafeAreaView>
                )}
                screenOptions={{
                    tabBarStyle: {
                        height: 60,
                        paddingBottom: 10,
                        paddingTop: 10,
                    },
                    tabBarShowLabel: false,
                }}
            >
                

                {/* 업로드페이지 */}
                <Tab.Screen name="Upload" component={UploadPage}
                options={{
                    tabBarIcon: ({ color, size, focused }) => (
                        <Image
                        source={require("../asset/mypage_icon.png")}
                        style={[styles.icon, { tintColor: focused ? colorchange : 'black'}]}/>
                    ),
                    headerShown: false,
                }}/>

                {/* 그룹추가페이지 */}
                <Tab.Screen name="MakeGroup" component={MakeGroup}
                options={{
                    tabBarIcon: ({ color, size, focused }) => (
                        <Image
                        source={require("../asset/nodepage_icon.png")}
                        style={[styles.icon, { tintColor: focused ? colorchange : 'black'}]}/>
                    ),
                    headerShown: false,
                }}/>

                {/* QR페이지 */}
                <Tab.Screen
                name="QR"
                component={QRPage}
                options={{
                    tabBarIcon: ({ color, size, focused }) => (
                        <Image
                        source={require("../asset/mainpage_icon.png")}
                        style={[styles.icon, { tintColor: focused ? colorchange : 'black'}]}/>
                    ),
                    headerShown: false,
                }}
                />

                {/* 그룹페이지 */}
                <Tab.Screen name="Group" component={GroupPage}
                options={{
                    tabBarIcon: ({ color, size, focused }) => (
                        <Image
                        source={require("../asset/alertpage_icon.png")}
                        style={[styles.icon, { tintColor: focused ? colorchange : 'black'}]}/>
                    ),
                    headerShown: false,
                }}/>

                {/* 설정페이지 */}
                <Tab.Screen name="Setting" component={SettingPage}
                options={{
                    tabBarIcon: ({ color, size, focused }) => (
                        <Image
                        source={require("../asset/settingpage_icon.png")}
                        style={[styles.icon, { tintColor: focused ? colorchange : 'black'}]}/>
                    ),
                    headerShown: false,
                }}/>
            </Tab.Navigator>
    );
};

const styles = StyleSheet.create({
    container: {
        backgroundColor: 'white',
    },

    icon: {
        width: 35,
        height: 35,
    },
});

export default BottomTabNavigation;
