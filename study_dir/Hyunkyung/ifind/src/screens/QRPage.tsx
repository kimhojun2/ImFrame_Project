import AsyncStorage from "@react-native-async-storage/async-storage";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import React, { useEffect, useState } from "react";
import { StyleSheet, Text, View } from "react-native";
import QRCode from "react-native-qrcode-svg";
import { SafeAreaProvider } from "react-native-safe-area-context";
import theme from "../styles/theme";

interface QRPageProps {
    navigation: NativeStackNavigationProp<any, 'QRPage'>;
}

export const QRPage = ({ navigation }: QRPageProps) => {

    const [uid, setUid] = useState<string | null>(null);

    useEffect(() => {
        const fetchUID = async () => {
            const storedUID = await AsyncStorage.getItem('userUID');
            if (storedUID) {
                setUid(storedUID);
            }
        };
        fetchUID();
    }, []);

    return (
        <SafeAreaProvider>
            <View style={styles.container}>
                <Text style={styles.title}>연동하기</Text>
                <View style={styles.separator} />
                <View style={styles.qrcode}>
                {uid && (
                    <QRCode
                        value={uid}
                        size={300}
                        color="black"
                        backgroundColor="white"
                    />
                )}
                <Text style={styles.subtitle}>액자 카메라에 QR코드를 비춰주세요</Text>
                </View>
            </View>
        </SafeAreaProvider>
    );
};


const styles = StyleSheet.create({
    container: {
        flex: 1,
        alignItems: 'center',
        backgroundColor: '#fff',
    },
    title:{
        paddingTop: 10,
        margin: 10,
        fontSize: 35,
        // fontWeight: "bold",
        color: theme.mainDarkGrey,
        fontFamily: theme.mainfont,
    },
    separator: {
        width: '90%',
        height: 1,
        backgroundColor: theme.navicolor,
        marginBottom: 5,
    },
    qrcode: {
        flex: 1,
        justifyContent: 'center',
    },
    subtitle: {
        paddingTop: 30,
        textAlign: 'center',
        color: theme.mainDarkGrey,
        fontFamily: theme.mainfont,
        fontSize: 22,
    }
});
