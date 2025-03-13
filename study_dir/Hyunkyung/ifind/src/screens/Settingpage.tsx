import AsyncStorage from "@react-native-async-storage/async-storage";
import firestore, { FirebaseFirestoreTypes } from '@react-native-firebase/firestore';
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import React, { useEffect, useState } from "react";
import { Image, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { signOut } from "../lib/auth";
import theme from "../styles/theme";


interface SettingPageProps {
    navigation: NativeStackNavigationProp<any, 'SettingPage'>;
}

interface Alert {
    time: FirebaseFirestoreTypes.Timestamp;
    type?: number;
    stop?: string;
}

export const SettingPage = ({ navigation }: SettingPageProps) => {
    const [userInfo, setUserInfo] = useState({ name: "", phone: "" });
    const [boardingTime, setBoardingTime] = useState("");
    const [estimatedArrivalTime, setEstimatedArrivalTime] = useState("");

    useEffect(() => {
        const fetchUserInfoAndLatestAlert = async () => {
            const uid = await AsyncStorage.getItem('userUID');
            if (uid) {
                const userDocRef = firestore().collection('users').doc(uid);
                
                userDocRef.onSnapshot(docSnapshot => {
                    if (docSnapshot.exists) {
                        const data = docSnapshot.data();
                        setUserInfo({
                            name: data?.name ?? "학생 이름",
                            phone: data?.phone ?? "기본 전화번호",
                        });
                
                        // alert 배열이 존재하는지 확인
                        if (data?.alert && Array.isArray(data.alert) && data.alert.length > 0) {
                            const latestAlert = data.alert.sort((a, b) => b.time.seconds - a.time.seconds)[0];
                            if (latestAlert && latestAlert.time?.seconds) {
                                const alertTime = new Date(latestAlert.time.seconds * 1000 + (9 * 60 * 60 * 1000));
                                const hours = alertTime.getUTCHours();
                                const minutes = alertTime.getUTCMinutes().toString().padStart(2, '0');
                                setBoardingTime(`${hours}:${minutes}`);
                            }
                        } else {
                            // alert 배열이 존재하지 않는 경우 처리
                            setBoardingTime("--");
                            console.log("alert 배열이 존재하지 않습니다.");
                        }
                    }
                });


                const pathDoc = await firestore().collection('morai').doc('path').get();
                if (pathDoc.exists) {
                    const totalDistance = pathDoc.data()?.total_distance;
                    if (totalDistance) {
                        calculateEstimatedArrivalTime(totalDistance);
                    } else {
                        setEstimatedArrivalTime("--");
                    }
                }
            }
        };

        fetchUserInfoAndLatestAlert();
}, []);

const calculateEstimatedArrivalTime = (totalDistance: number) => {
    const speedInMetersPerSecond = 40 * (1000 / 3600);
    const timeInSeconds = totalDistance / speedInMetersPerSecond;
    const currentTime = new Date();
    const estimatedArrivalDate = new Date(currentTime.getTime() + timeInSeconds * 1000 + (9 * 60 * 60 * 1000)); // Adjusting for UTC+9
    let estimatedHours = estimatedArrivalDate.getUTCHours();
    const estimatedMinutes = estimatedArrivalDate.getUTCMinutes().toString().padStart(2, '0');
    estimatedHours = estimatedHours % 24;
    setEstimatedArrivalTime(`약 ${estimatedHours}:${estimatedMinutes}`);
};

    const LogoutSubmit = async () => {
        try {
            await AsyncStorage.removeItem('userUID');
            await signOut();
            navigation.navigate('LoginPage', {name: 'LoginPage'});
        } catch (error) {
            console.error("로그아웃 실패:", error);
        }
    };

    const onItemPress = (item: string) => {
        console.log(`${item} 클릭됨`);
    };

    return (
        <View style={styles.container}>
            <Image source={require("../asset/mainicon.png")} style={styles.logo_image}/>
            <Text style={styles.title}>내 이름은 {userInfo.name}</Text>
            <Text style={styles.title}>{userInfo.phone}</Text>
            
            <TouchableOpacity
                style={styles.listItem}
                onPress={() => onItemPress("정보수정")}
            >
            <Text style={styles.listItemText}>사용자 정보 수정</Text>
            </TouchableOpacity>

            <TouchableOpacity
                style={styles.logout_button}
                onPress={LogoutSubmit}
            >
                <Text style={styles.buttonText}>로그아웃</Text>
            </TouchableOpacity>
        </View>
    )
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#fff',
        alignItems: 'center',
        justifyContent: 'center',
    },
    title: {
        fontSize: 40,
        fontFamily: theme.mainfont,
        // fontWeight: "bold",
        marginBottom: 20,
        color: theme.mainDarkGrey,
    },
    logo_image: {
        width: 80,
        height: 80,
        marginBottom: 10,
    },
    boxContainer: {
        flexDirection: 'row',
        justifyContent: 'space-around',
        width: '90%',
        height: '20%',
        marginBottom: 0,
    },
    box: {
        width: '30%',
        height: '65%',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 5,
        borderRadius: 20,
        marginBottom: 0,
    },
    boxtitle: {
        fontSize: 17,
        color: 'gray',
        fontFamily: theme.mainfont,
    },
    boxmain: {
        fontSize: 25,
        // fontWeight: 'bold',
        color: theme.mainDarkGrey,
        fontFamily: theme.mainfont,
    },
    listItem: {
        width: "90%",
        padding: 10,
        marginBottom: 20,
        borderBottomWidth: 0.5,
        borderColor: 'gray',
    },
    listItemText: {
        fontSize: 23,
        color: 'black',
        fontFamily: theme.mainfont,
    },
    logout_button: {
        marginTop: 30,
        width: '40%',
        alignItems: 'center',
        backgroundColor: theme.mainOrange,
        paddingHorizontal: 20,
        paddingVertical: 10,
        borderRadius: 40,
        shadowColor: "#000",
            shadowOffset: {
                width: 0,
                height: 2,
            },
            shadowOpacity: 0.25,
            shadowRadius: 4,
            elevation: 5,
            position: 'absolute',
            bottom: '10%',
    },
    buttonText: {
        fontFamily: theme.mainfont,
        padding: 5,
        color: 'black',
        fontSize: 23,
    },
    });